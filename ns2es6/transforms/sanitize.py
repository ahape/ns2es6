import os, re
from ..utils.transformer import Transformer
from ..utils.line_walker import LineWalker
from ..utils.logger import logger
from ..utils.trace_timer import TraceTimer

class _LineRemover(Transformer):
  def __init__(self, match_rx):
    super().__init__(match_rx, "<DELETE>")

class _Unindenter(Transformer):
  def __init__(self, match_rx):
    super().__init__(match_rx, "    ")

def should_exclude_file(file_path):
  return "node_modules" in file_path or \
      not file_path.endswith(".ts")

# Remove all '/// <reference />' comments
def create_reference_tag_remover():
  return Transformer(r"\/\/\/\s*\<reference ", "<DELETE>")

# Remove all jshint comments
def create_jshint_remover():
  return Transformer(r"\bjshint\b", "<DELETE>")

# Unindent everything 1x. Since everything will be reduced by one block scope
# (the namespace block that will be removed) this will make subsequent
# changes easier to grok
def create_unindenter():
  return Transformer(r"^\s{4}", "")

class _NamespaceRemover(Transformer):
  def analyze(self, text):
    res = super().analyze(text)
    # If we are going to remove the namespace start, then we have to also
    # remove the end
    if res and "<_NamespaceRemover>" in res:
      self.match_rx = re.compile(r"^\}")
    return res

def create_namespace_remover():
  return _NamespaceRemover(r"^namespace ", "<DELETE><_NamespaceRemover>")

def run(directory):
  timer = TraceTimer()
  timer.start()
  for root, dirs, files in os.walk(directory):
    for name in files:
      file_path = os.path.join(root, name)
      if should_exclude_file(file_path):
        continue
      logger.info("Sanitizing file %s", file_path)
      run_line_walker(file_path, True)
  timer.stop()
  logger.info("Operation took %s seconds", timer.elapsed)

def run_line_walker(file_path, commit_changes=False):
  walker = LineWalker(file_path, commit_changes)
  walker.add_transformer(create_reference_tag_remover())
  walker.add_transformer(create_jshint_remover())
  walker.add_transformer(create_unindenter())
  walker.add_transformer(create_namespace_remover())
  walker.walk()
