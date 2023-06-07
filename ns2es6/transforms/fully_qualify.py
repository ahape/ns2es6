import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import trace
from ns2es6.utils.symbol import Symbol
from ns2es6.utils import helpers
from ns2es6.transforms.collect_exports import NamespaceCollector

c_open_rx, c_close_rx = re.escape("/*"), re.escape("*/")
boundary_rx = re.compile(r"[^.a-zA-Z0-9_$]")

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

def re_count(pattern, text):
  return len(re.findall(pattern, text))

def is_base_if_ref(before):
  if re.search(r"\bclass\s+", before):
    b4 = before.rstrip()
    return b4.endswith("extends") or b4.endswith("implements")
  return True

def is_legit_match(match, before):
  return (
    # Exclude comments
    "//" not in before and
    # Exclude what may likely be a block comment
    re_count(c_open_rx, before) <= re_count(c_close_rx, before) and
    # If there's a mention of "class" then make sure *this* is not the class
    # name but rather something being extended
    is_base_if_ref(before))

class ExportReferenceReplacer(Transformer):
  def __init__(self, match_rx, ns_collector, exports):
    super().__init__(match_rx + r"(?![.?:])")
    self.exports = exports
    self.lookup = create_lookup(exports)
    self.ns_collector = ns_collector

  @property
  def current_ns(self):
    return self.ns_collector.current

  def word_has_potential(self, word):
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
          namespace = tuple(list(namespace)[:-1]) # Pop
    return best_choice["value"]

  def analyze(self, text):
    sb = ""
    left = text
    while left:
      if match := self.match_rx.search(left):
        s, e = match.start(), match.end()
        before = left[:s]
        last_boundary_index = -1
        if is_legit_match(match, before):
          for s_match in boundary_rx.finditer(before):
            last_boundary_index = s_match.start()
          if last_boundary_index > -1:
            last_boundary_index += 1
            before = left[:last_boundary_index]
            match_and_maybe_ns = left[last_boundary_index:e]
            if qualified := self.word_has_potential(match_and_maybe_ns):
              sb += before
              sb += qualified
        left = left[e:]
      else:
        break
    return sb + left if sb else text

@trace("fully qualify")
def run(directory, exports):
  symbols_rx = helpers.create_or_matcher([*map(lambda x: x.symbol, exports)])
  helpers.for_each_file(directory,
    lambda x: update_file(x, exports, symbols_rx))

def update_file(file_path, exports, symbols_rx, commit_changes=False):
  walker = LineWalker(file_path, commit_changes)
  ns_collector = NamespaceCollector()
  walker.add_transformer(ns_collector)
  walker.add_transformer(ExportReferenceReplacer(
    symbols_rx,
    ns_collector,
    exports))
  walker.walk()
