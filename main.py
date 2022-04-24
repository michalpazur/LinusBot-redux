import os
from utils.log import _log, _error
from dotenv import load_dotenv
import youtube.retrive_uploads as youtube
import screenshot.get_screenshot as screenshot
import facebook
import requests
from requests_oauthlib import OAuth1

twitter_url = "https://api.twitter.com/2"
twitter_upload_url = "https://upload.twitter.com/1.1/media/upload.json?media_category=tweet_image"

def main():
  with open("credits/credits.txt", encoding="utf-8") as _credits:
    for _line in _credits:
      print(_line.rstrip())
  
  print("")
  _log("Script started!")
  try:
    load_dotenv()
  except Exception as e:
    _error("Failed to load .env variables.", e)
    quit()
    
  _log("Successfully loaded .env variables.")
  playlist_id = youtube.retrive_uploads()
  video, timestamp = screenshot.get_screenshot(playlist_id)

  comment = "Screenshot taken at {} from video: \"{}\"\nhttps://youtu.be/{}".format(timestamp, video["title"], video["id"])
  try:
    facebook_client = facebook.GraphAPI(os.getenv("FACEBOOK_API_KEY"))
  
    with open("linus.png", "rb") as img:
      post_response = facebook_client.put_photo(img)
    post_id = post_response["post_id"]
    _log("Image posted to Facebook with id {}.".format(post_id))
    comment_response = facebook_client.put_comment(post_id, comment)
    comment_id = comment_response["id"]
    _log("Comment to post {} posted with id {}.".format(post_id, comment_id))
  except Exception as e:
    _error("Failed to post on Facebook! Trying Twitter...", e)
  
  try:
    auth = OAuth1(os.getenv("TWITTER_KEY"), os.getenv("TWITTER_KEY_SECRET"), os.getenv("TWITTER_TOKEN"), os.getenv("TWITTER_TOKEN_SECRET"))
    with open("linus.png", "rb") as img:
      image_upload_r = requests.post(twitter_upload_url, files={ "media": img }, auth=auth)
    photo_id = image_upload_r.json()["media_id"]

    tweet_response = requests.post(twitter_url + "/tweets", json={ "media": { "media_ids": [str(photo_id)] } }, auth=auth)
    tweet_id = tweet_response.json()["data"]["id"]
    _log("Posted tweet with id {}.".format(tweet_id))

    reply_response = requests.post(twitter_url + "/tweets", json={ "text": comment, "reply": { "in_reply_to_tweet_id": tweet_id }}, auth=auth)
    comment_id = reply_response.json()["data"]["id"]
    _log("Reply to tweet {} posted with id {}".format(tweet_id, comment_id))
  except Exception as e:
    _error("Failed to post on Twitter!", e)

if (__name__ == "__main__"):
  try:
    main()
  except Exception as e:
    _error("An uncaught error has occured.", e)
