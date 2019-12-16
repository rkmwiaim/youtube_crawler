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

def video_generator(query, max_results=50, start_time=None):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  search = youtube.search()
  page_token = None

  ids = set()

  while True:
    search_response = search.list(
      q=query,
      part="id,snippet",
      maxResults=max_results,
      pageToken=page_token,
      publishedAfter=start_time,
      order='date'
    ).execute()

    page_token = search_response.get('nextPageToken')
    print('page token: ', page_token)

    videos = []

    for search_result in search_response.get("items", []):
      if search_result["id"]["kind"] == "youtube#video":
        video_id = search_result["id"]["videoId"]

        if video_id not in ids:
          ids.add(video_id)

          title = search_result["snippet"]["title"]
          published_at = search_result["snippet"]["publishedAt"]

          video = [video_id, title, published_at]
          videos.append(video)

    yield videos

    if page_token is None or len(videos) == 0:
      break

  print('number of crawled videos: ', len(ids))


if __name__ == "__main__":
  gen = video_generator("유병언")
  for videos in gen:
    for v in videos:
      print(v)