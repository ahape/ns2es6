import re

class Transformer:
  def __init__(self, match_rx=None, replacement=None):
    if match_rx:
      self.match_rx = re.compile(match_rx)
    elif not hasattr(self, "match_rx"):
      self.match_rx = None
    self.replacement = replacement

  def analyze(self, text):
    if not self.match_rx:
      return None
    res = text
    if self.replacement is not None:
      res = self.match_rx.sub(self.replacement, text)
    if match := self.match_rx.search(text):
      self.handle_match(match[1] if match.groups() else None, match)
    return res

  def handle_match(self, capture, match):
    pass
