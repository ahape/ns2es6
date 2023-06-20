import os, re
from collections import namedtuple
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.trace_timer import trace
from ns2es6.utils.symbol import Symbol
from ns2es6.utils import helpers
from ns2es6.transforms.collect_exports import NamespaceCollector
from ns2es6.utils.logger import get_logger

logger = get_logger(__name__)

c_open_rx = re.escape("/*")
c_close_rx = re.escape("*/")
boundary_rx = re.compile(r"[^.a-zA-Z0-9_$]")
variable_rx = re.compile(r"[.a-zA-Z0-9_$]")
param_decs_rx = re.compile(r"[.a-zA-Z0-9_$ :?.,]")
starts_with_var_rx = re.compile(r"^[.a-zA-Z0-9_$].*")
ends_with_var_rx = re.compile(r".*[.a-zA-Z0-9_$]$")

extended_keywords = "|".join([
  "private",
  "public",
  "protected",
  "readonly",
]) + "|" + helpers.keywords

MatchResult = namedtuple("MatchResult", "sb succeeded after left")
MatchState = namedtuple("MatchState", "match before after sb left")

def create_lookup(exports):
  arr = [e.address for e in exports]
  memo = {}
  def criteria(addr, val):
    return addr.endswith(val) and \
        addr.split(".")[-1] == val.split(".")[-1]

  def lookup_fn(val):
    if val in memo:
      return memo[val]
    if found := [addr for addr in arr if criteria(addr, val)]:
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

class DeclarationCollector(Transformer):
  get_explicit_decs = re.compile(fr"(?:{helpers.keywords})\s+(\w+){boundary_rx.pattern}").search
  get_text_within_parens = re.compile(r"(?!if\s*)[\(](" +
                                      param_decs_rx.pattern +
                                      r"+?)[\)].*(?:\{|=>)").search

  def __init__(self):
    super().__init__()
    self.decs = set()

  @property
  def declarations(self):
    return list(self.decs)

  def analyze(self, text):
    if expl := self.get_explicit_decs(text):
      self.decs.add(expl[1])

    if params := self.get_text_within_parens(text):
      if decs := list(self.extract_decs_from_params(params[1])):
        self.decs = self.decs.union(set(decs))

  def extract_decs_from_params(self, params):
    for name in [param.split(":")[0] for param in params.split(",")]:
      if len(words := re.findall(r"(\w+)", name)) == 1:
        word = words[0]
        if not word.isdigit():
          yield word

class ExportReferenceReplacer(Transformer):
  def __init__(self, match_rx, ns_collector, exports, declarations):
    super().__init__(match_rx)
    self.exports = exports
    self.lookup = create_lookup(exports)
    self.ns_collector = ns_collector
    self.declarations = declarations

  @property
  def current_ns(self):
    return self.ns_collector.current

  def word_has_potential(self, name):
    best_choice = { "parents": 100, "value": None }
    if potentials := self.lookup(name):
      name = ns_tup(name)
      for potential in potentials:
        # max possible parents (no common ancenstor ns)
        parents = len(ns_tup(self.current_ns))
        if parents < best_choice["parents"]:
          best_choice["parents"] = parents
          best_choice["value"] = potential
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

  def analyze_match(self, state):
    def tidy_before():
      """
      if we need to get rid of what may have been a prior false-positive match
      """
      nonlocal sb, before
      last_ch = None
      if not before:
        while re.match(ends_with_var_rx, sb):
          if last_ch == "." and sb[-1] == ".":
            sb += "."
            return
          last_ch = sb[-1]
          sb = sb[:-1]
      else:
        while re.match(ends_with_var_rx, before):
          if last_ch == "." and sb[-1] == ".":
            sb += "."
            return
          last_ch = sb[-1]
          before = before[:-1]

    def tidy_after():
      nonlocal sb, after
      while starts_with_var_rx.match(after):
        sb += after[0]
        after = after[1:]

    match, before, after, sb, left = state
    value = match[1]
    e = match.end()
    last_boundary_index = -1

    if value not in self.declarations and self.is_legit_match(before, after):
      for s_match in re.split(boundary_rx, before):
        last_boundary_index = before.rindex(s_match)
      before = left[:last_boundary_index]
      match_and_maybe_ns = left[last_boundary_index:e]
      if qualified := self.word_has_potential(match_and_maybe_ns):
        tidy_before()
        sb += before
        sb += qualified
        tidy_after()
        return MatchResult(sb, True, after, left)
    return MatchResult(None, False, after, left)

  def analyze(self, text):
    sb = ""
    left = text
    after = None
    while left:
      if after:
        left = after
      if match := self.match_rx.search(left):
        before = left[:match.start()]
        after = left[match.end():]
        state = MatchState(match, before, after, sb, left)
        if (res := self.analyze_match(state)) and res.succeeded:
          sb = res.sb
          after = res.after
          continue
        sb += before + match[1]
      else:
        break
    return sb + left or text

  def is_legit_match(self, before, after):
    return (
      # Exclude if this is after a comment
      "//" not in before
      # Exclude if we're within a commit block (fuzzy)
      and re_count(c_open_rx, before) <= re_count(c_close_rx, before)
      # Exclude if this might be something getting assigned a value (fuzzy)
      # Bad: Baz = ...
      and not (after.lstrip().startswith("= ") and ":" not in before)
      # Exclude any combo of these before checks and after checks
      # Bad: Baz: ...
      # Bad: var foo { quux: 1, Baz: ... }
      # Bad: var foo { Baz: ... }
      # Bad: Baz, ...
      # Bad: { Baz, ...
      # Bad: , Baz, ...
      # Bad: Baz? ...
      and not ((not before.strip() or
                before.rstrip().endswith(",") or
                before.rstrip().endswith("{"))
               and (after.lstrip().startswith(":") or
                    after.lstrip().startswith("?") or
                    after.lstrip().startswith("(") or
                    after.lstrip().startswith(",")))
      # Bad: type Baz % ...
      and not (re.match(".*(" + extended_keywords + r")$", before.rstrip()) and
               (after.lstrip().startswith("=") or
                after.lstrip().startswith("(") or
                after.lstrip().startswith("<") or
                after.lstrip().startswith(":") or
                after.lstrip().startswith("{") or
                after.lstrip().startswith("of") or
                after.lstrip().startswith("in") or
                after.lstrip().startswith("instanceof") or
                after.lstrip().startswith("typeof") or
                after.lstrip().startswith("extends") or
                after.lstrip().startswith("implements")))
      # Bad: foo(Baz?: ...)
      # Bad: foo(Baz: ...)
      # Bad: foo(Baz, ...)
      and not (before.endswith("(") and
               (after.startswith("?") or
                after.startswith(":") or
                after.startswith(",")))
      # Bad: arr[x].Baz
      # Bad: foo?.Baz
      # Bad: foo!.Baz
      # Bad: fn().Baz
      # Bad: "Baz...
      # Bad: ...Baz"
      and not (before.endswith("].") or
               before.endswith("!.") or
               before.endswith("?.") or
               before.endswith(").") or
               before.endswith("\"") or
               after.lstrip().startswith("\""))
    )

@trace("fully qualify")
def run(directory, exports):
  symbols_rx = helpers.create_or_matcher([*map(lambda x: x.symbol, exports)])
  helpers.for_each_file(directory,
    lambda x: update_file(x, exports, symbols_rx, True))

def update_file(file_path, exports, symbols_rx, commit_changes=False):
  # First pass - collect declarations
  walker = LineWalker(file_path, commit_changes)

  dec_collector = DeclarationCollector()
  walker.add_transformer(dec_collector)
  walker.walk()

  # Second pass - fully qualify stuff
  walker = LineWalker(file_path, commit_changes)

  ns_collector = NamespaceCollector()
  walker.add_transformer(ns_collector)

  ref_replacer = ExportReferenceReplacer(
      symbols_rx,
      ns_collector,
      exports,
      dec_collector.declarations)
  walker.add_transformer(ref_replacer)
  walker.walk()
