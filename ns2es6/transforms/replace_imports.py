import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import TraceTimer
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
    rx = r"\b(" + "|".join(aliases) + ")(?=[" + re.escape(".[]()<>") + "])" if aliases else None
    super().__init__(rx)
    self.import_map = import_map

  def analyze(self, text):
    if self.match_rx and (match := self.match_rx.search(text)):
      try:
        self.replacement = self.import_map[match[1]]
      except KeyError:
        logger.error("KeyError -- %s %s", match.groups(), match.string)
    return super().analyze(text)

def run(directory):
  timer = TraceTimer()
  timer.start()
  helpers.for_each_file(directory, lambda f: update_file(f, True))
  timer.stop()
  logger.debug("Operation took %s seconds", timer.elapsed)

def update_file(file_path, commit_changes=False):
  logger.debug("Replacing import statements from file %s", file_path)
  write_file = commit_changes if isinstance(commit_changes, str) else \
      file_path if commit_changes else \
      False
  collector = ImportCollector()
  walker = LineWalker(file_path, write_file)
  walker.add_transformer(collector)
  walker.walk()
  walker = LineWalker(write_file or file_path, commit_changes)
  walker.add_transformer(ImportReplacer(collector.import_map))
  walker.walk()
