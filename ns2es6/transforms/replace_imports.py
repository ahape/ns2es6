import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import get_logger
from ns2es6.utils.trace_timer import trace
from ns2es6.utils import helpers

class ImportCollector(Transformer):
  def __init__(self):
    super().__init__(r"^\s*import\s+(\w+)\s+=\s+(\S+);$", "<DELETE>")
    self.imports = []

  def handle_match(self, capture, match):
    self.imports.append(match.groups())

  @property
  def import_map(self):
    return dict(self.imports)

class ImportReplacer(Transformer):
  def __init__(self, import_map):
    aliases = list(import_map.keys())
    before = re.escape(".")
    after = re.escape(".[]()<> ;,")
    negative_lookbehind = fr"(?<![{before}])"
    positive_lookahead = fr"(?=[{after}])"
    grouper = fr'\b({"|".join(aliases)})\b' # \b(foo|bar|baz)\b
    super().__init__(negative_lookbehind + grouper + positive_lookahead)
    self.import_map = import_map

  def analyze(self, text):
    if text.lstrip().startswith("//"):
      return text
    if self.match_rx and self.match_rx.search(text):
      for capture in list(set(self.match_rx.findall(text))):
        replacement = self.import_map[capture]
        text = re.sub(fr"\b({capture})\b", replacement, text)
    return text

@trace("replace imports")
def run(directory):
  helpers.for_each_file(directory, lambda f: update_file(f, True))

def update_file(file_path, commit_changes=False):
  collector = ImportCollector()
  walker = LineWalker(file_path, commit_changes)
  walker.add_transformer(collector)
  walker.walk()
  walker = LineWalker(commit_changes \
                        if isinstance(commit_changes, str) \
                        else file_path,
                      commit_changes)
  walker.add_transformer(ImportReplacer(collector.import_map))
  walker.walk()
