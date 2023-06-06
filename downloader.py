import tkinter as tk
from pytube.exceptions import VideoPrivate
from pytube.exceptions import VideoUnavailable
import pytube
from pytube import YouTube as YT
from googleapiclient.discovery import build
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


credentials = None

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

root = tk.Tk()
root.title("Youtube MP3 Downloader")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_width = 700
window_height = 200

# calculate the x and y coordinates to center the window
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

root.geometry(f"{window_width}x{window_height}+{x}+{y}")

data = []
ids = []
name = []
duration = []

with open('vid_data.txt', 'r', encoding="utf-8") as f:
    file_contents = f.read()
    data.append(file_contents)
    f.close()

result = [item.split('\n') for item in data]
result = result[0]

videos = int(((len(result) - 1) / 3))

# Separating into 3 lists
for i in range(videos):
    ids.append(result[0::3])

ids = ids[0]
ids = ids[0:-1]

for i in range(videos):
    name.append(result[1::3])

name = name[0]

for i in range(videos):
    duration.append(result[2::3])

duration = duration[0]


# Starter labels
text = tk.Label(root, text="Do you want to download this song?")
text.grid(row=0, column=1, columnspan=3)

label_ids = tk.Label(root, text=ids[0], anchor="center", pady=20)

label_name = tk.Label(root, text=name[0], anchor="center", pady=20)
label_name.grid(row=1, column=1)

label_duration = tk.Label(root, text=duration[0], anchor="center", pady=20)
label_duration.grid(row=2, column=1)

counter = 0


# No button function
def next_vid(song_number):
    global label_ids
    global label_name
    global label_duration
    global yes_button
    global no_button
    global counter

    label_name.grid_forget()
    label_duration.grid_forget()

    label_ids = tk.Label(text=ids[song_number - 1])
    label_name = tk.Label(text=name[song_number - 1])
    label_duration = tk.Label(text=duration[song_number - 1])

    no_button = tk.Button(root, text='Next Song', height=2, width=10, padx=35, pady=25,
                          command=lambda: next_vid(song_number + 1))

    yes_button.grid(row=3, column=0)
    no_button.grid(row=3, column=2)
    label_name.grid(row=1, column=1)
    label_duration.grid(row=2, column=1)

    counter += 1


# Yes button function
def download_vid(song_number):
    try:
        global yes_button

        youtube = build("youtube", "v3", credentials=credentials)
        pytube_download(song_number + counter)
        print("Download Complete...")
        youtube.videos().rate(id=ids[song_number + counter], rating="none").execute()
        print("Like revoked from video "+str(song_number + counter))

        yes_button = tk.Button(root, text="Download", height=2, width=10, padx=35, pady=25, command=lambda: download_vid(song_number))
    except pytube.exceptions.VideoPrivate:
        print("This video is private!")
    except KeyError:
        print("The video doesn't have an only_audio = True stream that you could download!")
    except VideoUnavailable:
        print("This video is unavailable.")


def pytube_download(song_number):
    link = ("https://youtu.be/"+ids[song_number])
    video = YT(link, use_oauth=True, allow_oauth_cache=True)
    vid = video.streams
    vid.filter(only_audio=True, file_extension="mp4", audio_codec="mp4a.40.5")
    if len(vid) == 1:
        vid[0].download(r"C:\YTDownloads")
    elif len(vid) == 0 or len(vid) is None:
        print("No youtube stream available with this category")
    else:
        vid.filter(only_audio=True, file_extension="mp4")
        vid[0].download(r"C:\YTDownloads")


# Buttons
no_button = tk.Button(root, text='Next Song', height=2, width=10, padx=35, pady=25, command=lambda: next_vid(2))
yes_button = tk.Button(root, text='Download', height=2, width=10, padx=35, pady=25, command=lambda: download_vid(0))


yes_button.grid(row=3, column=0)
no_button.grid(row=3, column=2)

root.mainloop()

# Progress Bar
# pb = ttk.Progressbar(root, orient='horizontal', mode='indeterminate', length=280)
# pb.pack()
