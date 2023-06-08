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

def outer_ns(s):
  parts = s.split(".")
  if len(parts) > 1:
    return ".".join(parts[:-1])
  return s

def ns_tup(s):
  return tuple(s.split("."))

def is_base_if_ref(before):
  if re.search(r"\bclass\s+", before):
    b4 = before.rstrip()
    return b4.endswith("extends") or b4.endswith("implements")
  return True

def is_legit_match(match, before, after):
  return (
    # Exclude comments
    "//" not in before and
    # Exclude what may likely be a block comment
    re_count(c_open_rx, before) <= re_count(c_close_rx, before) and
    # If there's a mention of "class" then make sure *this* is not the class
    # name but rather something being extended
    is_base_if_ref(before) and
    # Bad: var foo { quux: 1, Baz: ... }
    # Bad: var foo { Baz: ... }
    # Bad: Baz: ...
    not ((not before.strip() or
          before.rstrip().endswith(",") or
          before.rstrip().endswith("{"))
          and after.lstrip().startswith(":")) and
    # Bad: type Baz = ...
    not (re.search("(" + helpers.keywords + ")$", before.rstrip()) and
         (after.lstrip().startswith("=") or
          after.lstrip().startswith("(") or
          after.lstrip().startswith("<") or
          after.lstrip().startswith("{"))) and
    # Bad: foo(Baz?: ...)
    # Bad: foo(Baz: ...)
    not (before.endswith("(") and
         (after.startswith("?") or
          after.startswith(":")))
  )

class ExportReferenceReplacer(Transformer):
  def __init__(self, match_rx, ns_collector, exports):
    super().__init__(match_rx)
    self.exports = exports
    self.lookup = create_lookup(exports)
    self.ns_collector = ns_collector

  @property
  def current_ns(self):
    return self.ns_collector.current

  def word_has_potential(self, name):
    best_choice = { "parents": 100, "value": None }
    if potentials := self.lookup(name):
      name = ns_tup(name)
      for potential in potentials:
        namespace = ns_tup(self.current_ns)
        test = ns_tup(potential)
        parents = 1
        while namespace:
          if test == namespace + name:
            if parents < best_choice["parents"]:
              best_choice["parents"] = parents
              best_choice["value"] = potential
          parents += 1
          namespace = namespace[:-1]
    return best_choice["value"]

  def analyze(self, text):
    sb = ""
    left = text
    after = None
    while left:
      if after:
        left = after
      if match := self.match_rx.search(left):
        s, e = match.start(), match.end()
        before = left[:s]
        after = left[e:]
        last_boundary_index = -1
        if is_legit_match(match, before, after):
          for s_match in boundary_rx.finditer(before):
            last_boundary_index = s_match.start()
          if last_boundary_index > -1:
            last_boundary_index += 1
            _before = left[:last_boundary_index]
            match_and_maybe_ns = left[last_boundary_index:e]
            if qualified := self.word_has_potential(match_and_maybe_ns):
              #if outer_ns(qualified) != self.current_ns:
              sb += _before
              sb += qualified
              continue
        sb += before + match[1]
      else:
        break
    return sb + left or text

@trace("fully qualify")
def run(directory, exports):
  symbols_rx = helpers.create_or_matcher([*map(lambda x: x.symbol, exports)])
  helpers.for_each_file(directory,
    lambda x: update_file(x, exports, symbols_rx, True))

def update_file(file_path, exports, symbols_rx, commit_changes=False):
  walker = LineWalker(file_path, commit_changes)
  ns_collector = NamespaceCollector()
  walker.add_transformer(ns_collector)
  walker.add_transformer(ExportReferenceReplacer(
    symbols_rx,
    ns_collector,
    exports))
  walker.walk()
