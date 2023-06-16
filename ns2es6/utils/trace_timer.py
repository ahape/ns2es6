from time import time
from ns2es6.utils.logger import get_logger

logger = get_logger(__name__)

class TraceTimer:
  def __init__(self):
    self.duration = 0
    self.last_time = None
    self.running = False
  def start(self):
    if not self.running:
      self.last_time = time()
      self.running = True
  def stop(self):
    if self.running:
      self.duration += time() - self.last_time
      self.running = False
  def reset(self):
    self.duration = 0
    self.last_time = None
    self.running = False
  @property
  def elapsed(self):
    return f"{self.duration:f}"

def trace(name):
  def wrap_1(fn):
    def wrap_2(*args):
      timer = TraceTimer()
      timer.start()
      res = fn(*args)
      timer.stop()
      logger.info("'%s' took %s seconds", name, timer.elapsed)
      return res
    return wrap_2
  return wrap_1
