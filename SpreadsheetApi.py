from __future__ import print_function

import os.path
import pickle

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build

from functional import seq

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1-emqPYfy4mQV0Tuc7T_EvcVOUdmmWm83owMnNXg4xUY'
QUERY_RANGE = 'query!A:A'
SERVICE_ACCOUNT_FILE = 'youtube-crawler-spreadsheet.json'

class YoutubeSpreadsheet:
  def __init__(self, service_account_file=SERVICE_ACCOUNT_FILE):
    self.spreadsheet_resource = self.get_spreadsheet_resource()


  def get_spreadsheet_resource(self):
    """Shows basic usage of the Sheets API.
      Prints values from a sample spreadsheet.
      """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
      with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        # flow = InstalledAppFlow.from_client_secrets_file(
        #     'youtube-crawler-spreadsheet.json', SCOPES)
        # creds = flow.run_local_server(port=0)


        credentials = service_account.Credentials.from_service_account_file(
          SERVICE_ACCOUNT_FILE, scopes=SCOPES)
      # Save the credentials for the next run
      with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=credentials)

    # Call the Sheets API
    return service.spreadsheets()

  def get_sheets(self):
    spreadsheet_meta = self.spreadsheet_resource.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets_seq = seq(spreadsheet_meta['sheets'])
    return sheets_seq.map(lambda d: d['properties'])

  def get_sheet_titles(self):
    spreadsheet_meta = self.spreadsheet_resource.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets_seq = seq(spreadsheet_meta['sheets'])
    return sheets_seq.map(lambda d: d['properties']['title']).to_list()


  def read_queries(self):
    result = self.spreadsheet_resource.values().get(spreadsheetId=SPREADSHEET_ID,
                                                range=QUERY_RANGE).execute()
    values = result.get('values', [])

    if values is None:
      return []

    return seq(values).flat_map(lambda x: x).to_list()


  def add_sheet(self, sheet_name):
    update_body = {
      'requests': [
        {
          'addSheet': {
            'properties': {
              'title': sheet_name
            }
          }
        }
      ]
    }
    return self.spreadsheet_resource.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=update_body).execute()

  def get_sheet_id_from_res(self, add_sheet_res):
    return add_sheet_res['replies'][0]['addSheet']['properties']['sheetId']

  def add_sheet_with_video_header(self, sheet_name):
    add_sheet_res = self.add_sheet(sheet_name)
    sheet_id = self.get_sheet_id_from_res(add_sheet_res)
    self.add_video_header(sheet_id)

    return add_sheet_res


  def batch_append(self, sheet_id, data):
    rows = []

    for row in data:
      rows.append(
        {
          'values':
            [
              {'userEnteredValue': {'stringValue': c}} for c in row
            ]
        }
      )

    body = {
      'requests': [
        {
          'appendCells':
            {
              "sheetId": sheet_id,
              "rows": rows,
              "fields": '*'
            }
        }
      ]
    }
    return self.spreadsheet_resource.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()

  def add_header(self, sheet_id, header):
    return self.batch_append(sheet_id, [header])

  def add_video_header(self, sheet_id):
    header = ['video id', 'title', 'published at']
    return self.add_header(sheet_id, header)

  def insert_empty_rows_at_head(self, sheet_id, num_rows):
    body = {
      'requests': [
        {
          'insertDimension': {
            'range': {
              'sheet_id': sheet_id,
              'dimension': 'ROWS',
              'startIndex': 1,
              'endIndex': 1 + num_rows
            }
          }
        }
      ]
    }

    return self.spreadsheet_resource.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()


  def update_data_at_head(self, sheet_id, data):
    rows = []

    for row in data:
      rows.append(
        {
          'values':
            [
              {'userEnteredValue': {'stringValue': c}} for c in row
            ]
        }
      )

    body = {
      'requests': [
        {
          'updateCells':
            {
              "rows": rows,
              "fields": '*',
              "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1,
                "endRowIndex": 1 + len(data),
                "startColumnIndex": 0,
                "endColumnIndex": len(data[0])
              }
            }
        }
      ]
    }

    return self.spreadsheet_resource.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()


  def insert_data_at_head(self, sheet_id, data):
    self.insert_empty_rows_at_head(sheet_id, len(data))
    return self.update_data_at_head(sheet_id, data)

  def get_last_video_date(self, sheet_name):
    return self.spreadsheet_resource.values().get(spreadsheetId=SPREADSHEET_ID, range=sheet_name + "!C2").execute()['values'][0][0]


def main():
  youtube_spreadsheet = YoutubeSpreadsheet()
  titles = youtube_spreadsheet.get_sheet_titles()

if __name__ == '__main__':
  main()
