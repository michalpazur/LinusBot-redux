from time import strftime, time_ns
import traceback

def format_time():
  return "{}:{}".format(strftime("%H:%M:%S"), get_ms())

def get_ms():
  ms_time = int(time_ns() / 1000000) % 1000
  return str(ms_time).zfill(3)

def _log(message: str): 
  print("INFO {}: {}".format(format_time(), message))

def _warn(message: str):
  print("WARN {}: {}".format(format_time(), message))

def _error(message: str, e: Exception = None):
  print("ERROR {}: {}".format(format_time(), message))
  if (e is not None):
    print(traceback.format_exc())