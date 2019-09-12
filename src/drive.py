from __future__ import print_function
import pickle
import io
import os.path

# if you don't have root privelages
import sys
# Replace the path below to wherever pip3 --user installs dependencies
sys.path.insert(1, '/Users/michaeljoconnell/Library/Python/3.7/bin')

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload

# from google_drive_downloader import GoogleDriveDownloader as gd

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def download_file(service, file_id, local_fd):
    """Download a Drive file's content to the local filesystem.

    Args:
    service: Drive API Service instance.
    file_id: ID of the Drive file that will downloaded.
    local_fd: io.Base or file object, the stream that the Drive file's
        contents will be written to.
    """
    request = service.files().get_media(fileId=file_id)
    media_request = MediaIoBaseDownload(local_fd, request)

    while True:
        try:
            download_progress, done = media_request.next_chunk()
        except:
            print('An error occurred')
            return
        if download_progress:
            print('Download Progress: %d%%' % int(download_progress.progress() * 100))
        if done:
            print('Download Complete')
            return

def getPath():
    path = input('\nPlease input the path to the directory that you want to download the images to: ')
    path = path.strip()
    if not path.endswith('/') or not path.endswith('\\'):
        path += '/'
    return path

def getItems(local_path):

    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
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
            flow = InstalledAppFlow.from_client_secrets_file(
                '../credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    query = "mimeType='application/vnd.google-apps.folder'"
    folderID = callDriveAPI(service, local_path, query, True)
    query = folderID
    # callDriveAPI(service, local_path, query, False)

def callDriveAPI(service, local_path, query, findFolder):
    # Call the Drive v3 API
    page_token = None
    while True:
        results = service.files().list(q = query,
                                       pageSize=1000,
                                       fields="nextPageToken,files(id, name)",
                                       pageToken=page_token).execute()
        items =  results.get('files', [])
        for item in items:
            if (findFolder) and ("Cat Photos" in item['name']):
                print ("Found Cat Photos")
                return item['id']
            elif (not findFolder):
                print(u'{0} ({1})'.format(item['name'], item['id']))
                file_id = item['id']
                f = open(local_path + item['name'], 'wb')
                download_file(service, file_id, f)
        page_token = results.get('nextPageToken', None)
        if page_token is None:
            return None

def main():
    path = getPath()
    getItems(path)

if __name__ == '__main__':
    main()