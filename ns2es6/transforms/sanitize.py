import os
from ..utils.transformer import Transformer
from ..utils.line_walker import LineWalker
from ..utils.logger import logger
from ..utils.trace_timer import TraceTimer

class _LineRemover(Transformer):
  def __init__(self, match_rx):
    super().__init__(match_rx, "<DELETE>")

def should_exclude_file(file_path):
  return "node_modules" in file_path or \
      not file_path.endswith(".ts")

def run(directory):
  timer = TraceTimer()
  timer.start()
  for root, dirs, files in os.walk(directory):
    for name in files:
      file_path = os.path.join(root, name)
      if should_exclude_file(file_path):
        continue
      logger.info("Sanitizing file %s", file_path)
      remove_all_comments(file_path, True)
  timer.stop()
  logger.info("Operation took %s seconds", timer.elapsed)

def remove_all_comments(file_path, commit_changes=False):
  reference_remover = _LineRemover(r"\/\/\/\s*\<reference ")
  jshint_remover = _LineRemover(r"\bjshint\b")
  #tslint_remover = _LineRemover(r"\btslint\b")

  walker = LineWalker(file_path, commit_changes)
  walker.add_transformer(reference_remover)
  walker.add_transformer(jshint_remover)
  #walker.add_transformer(tslint_remover)

  walker.walk()
