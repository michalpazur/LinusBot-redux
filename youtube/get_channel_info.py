import utils.api_client as api_client
from utils.log import _log, _error

def get_channel_info():
  client = api_client.get_client()
  _log("Downloading channel data...")
  params = { "forUsername": "LinusTechTips", "part": "contentDetails,statistics" }
  
  try:
    response = client.get(api_client.base_url + "/channels", params=params)
    if (response.status_code != 200):
      _error("Channel data request finished with code {}. Shutting down...".format(response.status_code))
      quit()
    else:
      json = response.json()
      channel_data = json["items"][0]
      uploads_playlist = channel_data["contentDetails"]["relatedPlaylists"]["uploads"]
      video_count = channel_data["statistics"]["videoCount"]
      _log("Successfully downloaded channel data. Total uploads: {}, uploads playlist id: {}".format(video_count, uploads_playlist))
      return int(video_count), uploads_playlist
  except Exception as e:
    _error("Unknown error has occured while downloading channel data. Shutting down...", e)
    quit()