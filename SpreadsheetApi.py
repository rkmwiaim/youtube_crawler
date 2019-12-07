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
SAMPLE_SPREADSHEET_ID = '1l9p_UpqsAU3ByqDIm4koHnRSVnB2eHZBJkPwIsWmwuo'
SAMPLE_RANGE_NAME = 'query!A:A'


def get_sheet_titles(spreadsheet_resource):
  spreadsheet_meta = spreadsheet_resource.get(spreadsheetId=SAMPLE_SPREADSHEET_ID).execute()
  sheets_seq = seq(spreadsheet_meta['sheets'])
  return sheets_seq.map(lambda d: d['properties']['title']).to_list()


def read_queries(spreadsheets_meta):
  result = spreadsheets_meta.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                          range=SAMPLE_RANGE_NAME).execute()
  values = result.get('values', [])

  if values is None:
    return []

  return seq(values).flat_map(lambda x: x).to_list()


def add_sheet(spreadsheets_meta, sheet_name):
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
  spreadsheets_meta.batchUpdate(spreadsheetId=SAMPLE_SPREADSHEET_ID, body=update_body).execute()


def main():
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
  spreadsheets_meta = service.spreadsheets()

  sheet_titles = get_sheet_titles(spreadsheets_meta)
  print(sheet_titles)

  queries = read_queries(spreadsheets_meta)
  print(queries)

  add_sheet(spreadsheets_meta, 'dfg')

  # result = spreadsheets_meta.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
  #                             range=SAMPLE_RANGE_NAME).execute()
  # values = result.get('values', [])
  #
  # if not values:
  #     print('No data found.')
  # else:
  #     print('Name, Major:')
  #     for row in values:
  #         # Print columns A and E, which correspond to indices 0 and 4.
  #         print(row)


if __name__ == '__main__':
  main()
