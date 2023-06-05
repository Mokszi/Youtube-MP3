import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

credentials = None
data = []

# token.pickle stores the user's credentials from previously successful logins
if os.path.exists('token.pickle'):
    print('Loading Credentials From File...')
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)

# If there are no valid credentials available, then either refresh the token or log in.
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print('Refreshing Access Token...')
        credentials.refresh(Request())
    else:
        print('Fetching New Tokens...')
        flow = InstalledAppFlow.from_client_secrets_file('client_secret.json',
                                                         scopes=["https://www.googleapis.com/auth/youtube.readonly",
                                                                 "https://www.googleapis.com/auth/youtube",
                                                                 "https://www.googleapis.com/auth/youtube.force-ssl"])

        flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
        credentials = flow.credentials

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as f:
            print('Saving Credentials for Future Use...')
            pickle.dump(credentials, f)

youtube = build("youtube", "v3", credentials=credentials)

pagetokens = ["", "CDIQAA", "CGQQAQ", "CJYBEAE", "CJYBEAA"]

global request

path = "/Users/Geri/PycharmProjects/Downloader"
check_file = os.path.exists(path)

if not check_file:
    with open("vid_data.txt", "xt"):
        pass
else:
    for i in range(len(pagetokens)):
        request = youtube.videos().list(part="snippet,contentDetails,statistics", myRating="like", maxResults=50,
                                        pageToken=pagetokens[i]).execute()

        # Getting title, id and duration of liked video
        for item in request["items"]:
            global vid_title
            global vid_id
            global vid_time

            vid_title = item["snippet"]["title"]
            vid_id = item["id"]
            vid_time = item["contentDetails"]["duration"]

            vid_time = vid_time.replace("H", " hour ")
            vid_time = vid_time.replace("M", " minute ")
            vid_time = vid_time.replace("S", " second ")
            vid_time = vid_time[2:]

            data.append(vid_id + "\n")
            data.append(vid_title + "\n")
            data.append(vid_time + "\n")

# Writing the data into the file
with open('vid_data.txt', 'w', encoding="utf-8") as f:
    for i in range(len(data)):
        f.write(data[i])
f.close()
