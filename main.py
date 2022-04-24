from utils.log import _log, _error
from dotenv import load_dotenv
import youtube.retrive_uploads as youtube

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
  youtube.retrive_uploads()

if (__name__ == "__main__"):
  try:
    main()
  except Exception as e:
    _error("An uncaught error has occured.", e)
