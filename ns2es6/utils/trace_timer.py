from time import time

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
