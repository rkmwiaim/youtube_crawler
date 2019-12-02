#!/usr/bin/python

from apiclient.discovery import build

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
with open('developer_key', 'r') as f:
  DEVELOPER_KEY = f.readline().strip()

print('developer key', DEVELOPER_KEY)
print('------------------------------------------------------------------------')
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(query):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  search = youtube.search()
  page_token = None

  ids = set()

  while True:
    search_response = search.list(
      q=query,
      part="id,snippet",
      maxResults=50,
      pageToken=page_token
    ).execute()

    videos = []

    page_token = search_response.get('nextPageToken')
    print('page token: ', page_token)

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
      if search_result["id"]["kind"] == "youtube#video":
        video_id = search_result["id"]["videoId"]
        video = "{0}\t{1}\t{2}".format(search_result["snippet"]["publishedAt"], search_result["snippet"]["title"],
                                       video_id)

        if video_id in ids:
          print('duplicate id:', video_id)

        ids.add(video_id)
        print(video)

    if page_token is None:
      break

    print('------------------------------------------------------------------------')

  # print("Videos:\n", "\n".join(videos), "\n")


if __name__ == "__main__":
  youtube_search("장씨세가 호위무사")