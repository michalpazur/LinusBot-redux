import utils.api_client as api_client
from utils.log import _log, _warn, _error
import youtube.get_channel_info as channel
import json

def download_page(playlist_id, page_token: str = None, max_results = 50):
  params = { "playlistId": playlist_id, "part": "snippet,contentDetails", "maxResults": max_results, "fields": "items(contentDetails,snippet(title)),nextPageToken" }
  if (page_token is not None):
    params["pageToken"] = page_token

  client = api_client.get_client()
  response = client.get(api_client.base_url + "/playlistItems", params=params)
  if (response.status_code != 200):
    raise Exception("Downloading page finished with code {}.".format(response.status_code))
  else:
    r_json = response.json()
    if ("nextPageToken" in r_json):
      next_page_token = r_json["nextPageToken"]
    else:
      next_page_token = None
    videos = []
    for item in r_json["items"]:
      video = { "title": item["snippet"]["title"], "id": item["contentDetails"]["videoId"], "published_at": item["contentDetails"]["videoPublishedAt"] }
      videos.append(video)
    return videos, next_page_token

def handle_download(playlist_id: str, video_count: int, cached_videos_length: int, uploaded_videos: list):
  pages_to_download = int((video_count - cached_videos_length) / 50) + 1
  
  next_page_token = None
  for i in range(pages_to_download):
    _log("Downloading page {} of {}...".format(i + 1, pages_to_download))
    max_results = 50 if i + 1 < pages_to_download else (video_count - cached_videos_length) % 50
    try:
      videos, next_page_token = download_page(playlist_id, next_page_token, max_results)
      copied_id = None
      for video_new in videos:
        # Oh god, I'm sorry for this nested breaks mess
        if (copied_id is not None):
          break
        for video_cached in uploaded_videos:
          if (video_cached["id"] == video_new["id"]):
            copied_id = video_new["id"]
            break

      if (copied_id is not None):
        _warn("Found duplicate video id ({}). Caching all videos again...".format(copied_id))
        return handle_download(playlist_id, video_count, 0, []) # Break the main loop and start with empty array
      else:
        uploaded_videos.extend(videos)
    except Exception as e:
      _error("Error has occurred while caching videos. Shutting down...", e)
      quit()
    
  return uploaded_videos

def retrive_uploads():
  video_count, uploads_playlist = channel.get_channel_info()
  try:
    with open("youtube/{}.json".format(uploads_playlist), encoding="utf-8") as f:
      uploaded_videos = json.load(f)
  except:
    _warn("No saved uploads found.")
    uploaded_videos = []

  cached_videos_length = len(uploaded_videos)

  if (cached_videos_length > video_count):
    _warn("Cached videos array is longer than video count ({} vs. {}). Caching all videos...".format(cached_videos_length, video_count))
    cached_videos_length = 0
    uploaded_videos = []
  elif (cached_videos_length == video_count):
    _log("Found {} videos. No need to update.".format(cached_videos_length))
    return uploads_playlist
  
  videos = handle_download(uploads_playlist, video_count, cached_videos_length, uploaded_videos)

  with open("youtube/{}.json".format(uploads_playlist), "w", encoding="utf-8") as f:
    json.dump(videos, f, indent=2)
    _log("Successfully saved cached videos to youtube/{}.json!".format(uploads_playlist))

  return uploads_playlist