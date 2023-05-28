import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import TraceTimer
from ns2es6.utils.symbol import Symbol
from ns2es6.utils import helpers
from ns2es6.transforms.collect_exports import NamespaceCollector

c_open_rx, c_close_rx = re.escape("/*"), re.escape("*/")
word_splitter_rx = re.compile(r"[^.a-zA-Z0-9_$]")

def create_lookup(exports):
  arr = [e.address for e in exports]
  memo = {}
  def lookup_fn(val):
    if val in memo:
      return memo[val]
    found = [addr for addr in arr if addr.endswith(val)]
    if found:
      ret = memo[val] = found[0]
      return ret
    return None
  return lookup_fn

def extract_words(text):
  return word_splitter_rx.split(text)

def re_count(pattern, text):
  return len(re.findall(pattern, text))

def is_legit_match(match):
  text = match.string.rstrip()
  start, end = match.start(), match.end()
  before, after = text[:start], text[end:]
  return (
    not before.endswith("this.") and
    not after.startswith(":") and
    "export " not in before and
    "//" not in before and
    re_count(c_open_rx, before) <= re_count(c_close_rx, before))

def ok_to_replace(word, addr):
  return addr != word and len(word.split(".")) > 1

class ExportReferenceReplacer(Transformer):
  def __init__(self, match_rx, ns_collector, exports, file_path):
    super().__init__(match_rx)
    self.exports = exports
    self.lookup = create_lookup(exports)
    self.current_file = file_path
    self.ns_collector = ns_collector

  @property
  def current_ns(self):
    return self.ns_collector.current

  def word_has_potential(self, word):
    return not word.startswith(".") and self.lookup(word)

  def analyze(self, text):
    for match in self.match_rx.finditer(text):
      if match and is_legit_match(match):
        symbol = match[1]
        words = extract_words(text)
        for word in words:
          if symbol in word and (addr := self.word_has_potential(word)):
            if ok_to_replace(word, addr):
              text = text.replace(word, addr)
            else:
              pass
    return text

def create_matcher(exports):
  symbols = list(set(map(lambda x: x.symbol, exports)))
  return r"\b(" + "|".join(symbols) + r")\b"

def run(directory, exports):
  timer = TraceTimer()
  timer.start()
  symbols_rx = create_matcher(exports)
  helpers.for_each_file(directory,
    lambda x: update_file(x, exports, symbols_rx))
  timer.stop()
  logger.debug("Operation took %s seconds", timer.elapsed)

def update_file(file_path, exports, symbols_rx):
  walker = LineWalker(file_path, True)
  ns_collector = NamespaceCollector()
  walker.add_transformer(ns_collector)
  walker.add_transformer(ExportReferenceReplacer(
    symbols_rx,
    ns_collector,
    exports,
    file_path))
  walker.walk()
