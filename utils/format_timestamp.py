def format_timestamp(timestamp: int):
  hours = int(timestamp / 3600)
  minutes = int(timestamp / 60) % 60
  seconds = timestamp % 60
  formatted_timestamp = "{}:{}".format(str(minutes).zfill(2), str(seconds).zfill(2))
  if (hours > 0):
    formatted_timestamp = "{}:".format(hours) + formatted_timestamp
  return formatted_timestamp
