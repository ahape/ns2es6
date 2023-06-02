import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import trace
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
    if found := [addr for addr in arr if addr.endswith(val)]:
      ret = memo[val] = found
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
    (" extends " in before if " export class " in before else " export " not in before) and
    "//" not in before and
    re_count(c_open_rx, before) <= re_count(c_close_rx, before))

class ExportReferenceReplacer(Transformer):
  def __init__(self, match_rx, ns_collector, exports):
    super().__init__(match_rx)
    self.exports = exports
    self.lookup = create_lookup(exports)
    self.ns_collector = ns_collector

  @property
  def current_ns(self):
    return self.ns_collector.current

  def word_has_potential(self, word):
    if word.startswith("."):
      return None
    best_choice = { "parents": 100, "value": None }
    if potentials := self.lookup(word):
      word = tuple(word.split("."))
      for potential in potentials:
        namespace = tuple(self.current_ns.split("."))
        pot = tuple(potential.split("."))
        parents = 1
        while namespace:
          if pot == namespace + word:
            if parents < best_choice["parents"]:
              best_choice["parents"] = parents
              best_choice["value"] = potential
          parents += 1
          namespace = tuple(list(namespace)[:-1]) # (granny, papa, son) -> (granny, papa)
    return best_choice["value"]

  def analyze(self, text):
    for match in self.match_rx.finditer(text):
      if match and is_legit_match(match):
        symbol = match[1]
        words = extract_words(text)
        for word in words:
          if symbol in word and (full := self.word_has_potential(word)) and word in full:
            text = re.sub(fr"(?<![.])\b({word})\b(?=[^.:?])", full, text)
    return text

@trace("fully qualify")
def run(directory, exports):
  symbols_rx = helpers.create_or_matcher([*map(lambda x: x.symbol, exports)])
  helpers.for_each_file(directory,
    lambda x: update_file(x, exports, symbols_rx))

def update_file(file_path, exports, symbols_rx):
  walker = LineWalker(file_path, True)
  ns_collector = NamespaceCollector()
  walker.add_transformer(ns_collector)
  walker.add_transformer(ExportReferenceReplacer(
    symbols_rx,
    ns_collector,
    exports))
  walker.walk()
