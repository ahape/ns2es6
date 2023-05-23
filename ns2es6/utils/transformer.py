import re

class Transformer:
  def __init__(self, match_rx=None, replacement=None):
    if match_rx:
      self.match_rx = re.compile(match_rx)
    self.replacement = replacement

  def analyze(self, text):
    if not self.match_rx:
      return None
    if self.replacement is not None:
      return self.match_rx.sub(self.replacement, text)
    if match := self.match_rx.search(text):
      self.handle_match(match[1]) # Capture is expected
    return text

  def handle_match(self, match):
    ...
