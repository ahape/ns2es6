import re

class Transformer:
  match_rx = None
  replacement = None

  def __init__(self, match_rx, replacement=None):
    self.match_rx = re.compile(match_rx)
    self.replacement = replacement

  def analyze(self, text):
    if not self.match_rx:
      return None
    if self.replacement:
      return self.match_rx.sub(self.replacement, text)
    return self.match_rx.search(text, flags=re.DOTALL)
