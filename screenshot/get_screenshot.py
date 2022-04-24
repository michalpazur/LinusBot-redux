import json
import random
import os
import time
from utils.log import _log, _warn, _error
from utils.format_timestamp import format_timestamp
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

max_retries = 5

def get_screenshot(playlist_id: str):
  with open("youtube/{}.json".format(playlist_id), encoding="utf_8") as f:
    uploads_playlist = json.load(f)
  
  driver = webdriver.Chrome(ChromeDriverManager().install())
  driver.set_window_rect(width=1440, height=900)
  driver.get("file://{}/player.html".format(os.getcwd()))

  screenshot_taken = False
  retry = 0
  while (not screenshot_taken and retry <= max_retries):
    if (retry > 0):
      _warn("Failed to take a screenshot. Retry {}/{}.".format(retry, max_retries))

    video = random.choice(uploads_playlist)
    video_id = video["id"]

    _log("Selected video with id {}.".format(video_id))
    
    driver.switch_to.default_content()
    driver.execute_script("player.loadVideoById('{}');".format(video_id))
    player_frame = driver.find_element_by_id("player")
    driver.switch_to.frame(player_frame)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Play (k)']"))).click()
    try:
      WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Subtitles/closed captions (c)']"))).click()
    except:
      _warn("No closed captions button found.")
      retry += 1
      continue

    driver.switch_to.default_content()
    video_duration = 0
    duration_retries = 0
    while (duration_retries < 5 and video_duration == 0):
      video_duration = int(driver.execute_script("return player.getDuration();"))
      if (video_duration == 0):
        time.sleep(0.5)
        duration_retries += 1
    
    if (video_duration == 0):
      _warn("Unable to get video duration.")
      retry += 1
      continue
    
    # Skip intro and outro for videos longer than 60 seconds
    range_start = 10 if video_duration > 60 else 0
    range_end = video_duration - 30 if video_duration > 60 else video_duration - 10
    timestamp = random.randint(range_start, range_end)
    
    formatted_timestamp = format_timestamp(timestamp)
    _log("Seeking to {}.".format(formatted_timestamp))
    driver.execute_script("player.seekTo({}, true);".format(timestamp))
    
    # Double click the player to hide the UI
    driver.switch_to.frame(player_frame)
    player = driver.find_element_by_class_name("html5-video-player")
    player.click()
    player.click()
    try:
      WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CSS_SELECTOR, "button[aria-label='Play (k)']"))) # Wait for the play button to be hidden
    except:
      _warn("Play button was not hidden.")
      retry += 1
      continue
    try:
      WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CLASS_NAME, "ytp-paid-content-overlay-text"))) # Wait for the paid promotion banner to be hidden
    except:
      _warn("Paid promotion banner was not hidden.")
      retry += 1
      continue

    player.screenshot("linus.png")
    screenshot_taken = True
    _log("Successfully taken a screenshot!")

  driver.quit()

  if (not screenshot_taken):
    _error("Script has been unable to take a screenshot. Shutting down...")
    quit()

  return video, formatted_timestamp