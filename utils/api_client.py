import requests
import os

base_url = "https://www.googleapis.com/youtube/v3"

def get_client():
  r = requests.Session()
  r.params = { "key": os.getenv("GOOGLE_KEY") }
  return r