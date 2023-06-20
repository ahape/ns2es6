import logging

def get_logger(name, level="info"):
  logging.basicConfig()
  logger = logging.getLogger(name)
  set_log_level(logger, level)
  return logger

def set_log_level(logger, level):
  match level.lower().strip():
    case "debug":
      logger.setLevel(logging.DEBUG)
    case "info" | _:
      logger.setLevel(logging.INFO)
