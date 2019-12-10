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
QUERY_RANGE_NAME = 'query!A:A'


def get_spreadsheet_resource():
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
      SERVICE_ACCOUNT_FILE = 'youtube-crawler-spreadsheet.json'

      credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
      pickle.dump(creds, token)

  service = build('sheets', 'v4', credentials=credentials)

  # Call the Sheets API
  return service.spreadsheets()


def get_sheet_titles(spreadsheet_resource):
  spreadsheet_meta = spreadsheet_resource.get(spreadsheetId=SPREADSHEET_ID).execute()
  sheets_seq = seq(spreadsheet_meta['sheets'])
  return sheets_seq.map(lambda d: d['properties']['title']).to_list()


def read_queries(spreadsheets_resource):
  result = spreadsheets_resource.values().get(spreadsheetId=SPREADSHEET_ID,
                                              range=QUERY_RANGE_NAME).execute()
  values = result.get('values', [])

  if values is None:
    return []

  return seq(values).flat_map(lambda x: x).to_list()


def add_sheet(spreadsheets_resource, sheet_name):
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
  return spreadsheets_resource.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=update_body).execute()


def batch_append(spreadsheets_resource, sheet_id, data):
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
  return spreadsheets_resource.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()



def main():
  spreadsheets_resource = get_spreadsheet_resource()

  test_data = [
    ['yjcPdcUxyh8', '보겸 장삐쭈 양팡 워크맨 ㅂㅇㄹ', '2019-12-10T11:11:03.000Z'],
    [
      'ZtU-z5-dzOY', '워크맨 장성규보다 더 빡쎈 고냥이의 일일 인턴 체험기! 직장상사에게 예쁨받는 노하우 고냥이가 직접 알려줌 ㅣ춤추는고냥 EP.15ㅣ',
      '2019-12-10T09:00:08.000Z'],
    ['yWbNj-tcWgI', '[2019 학술제] 인제대학교 신문방송학과 워크맨', '2019-12-09T20:17:25.000Z']
  ]
  batch_append(spreadsheets_resource, 1138121828, test_data)


if __name__ == '__main__':
  main()
