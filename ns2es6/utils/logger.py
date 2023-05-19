import os
from logging import getLogger, DEBUG

logger = getLogger()
if os.getenv("DEBUG", None):
  logger.setLevel(DEBUG)
