from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class FetchSheets(object):
    # If modifying these scopes, delete the file token.pickle
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1wg-s4_Lz2Stil6spQEYFdZaBEp8nWW26gVyfHqvcl8s'
    HAUPT_RANGE_NAME = 'Haupt!A5:P'
    BUNDESLAND_RANGE_NAME = 'Statistics!B1:J17'

    """ Shows basic usage of the Sheets API
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'sheetsApi/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)

    def Haupt(self):
        # Call the Sheets API
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                    range=self.HAUPT_RANGE_NAME).execute()
        values = result.get('values', [])
        return values

    def Bundesland(self):
        # Call the Sheets API
        sheet = self.service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                    range=self.BUNDESLAND_RANGE_NAME).execute()
        values = result.get('values', [])
        return values

if __name__ == '__main__':

    FS = FetchSheets()
    nuts3 = FS.Haupt()
    nuts1 = FS.Bundesland()
