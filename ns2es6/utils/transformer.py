import re

class Transformer:
  rx = None

  def __init__(self, rx):
    self.rx = rx

  def match(self, text):
    return re.search(self.rx, text, flags=re.DOTALL)

  def replace(self, value, text):
    return re.sub(self.rx, value, text)
