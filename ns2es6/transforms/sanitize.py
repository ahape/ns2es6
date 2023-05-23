import os, re
from ..utils.transformer import Transformer
from ..utils.line_walker import LineWalker
from ..utils.logger import logger
from ..utils.trace_timer import TraceTimer

class _Unindenter(Transformer):
  def __init__(self, walker):
    super().__init__(r"^\s{4}", "")
    self.walker = walker
  def analyze(self, text):
    res = super().analyze(text)
    # Only unindent if we've removed the outermost 'namespace' block
    if self.walker.check_tags_for(_NamespaceRemover.tag):
      return res
    return text

class _NamespaceRemover(Transformer):
  tag = "<@NamespaceRemover@>"

  def __init__(self):
    super().__init__(r"^namespace ", f"<DELETE>{self.tag}")

  def analyze(self, text):
    res = super().analyze(text)
    # If we are going to remove the namespace start, then we have to also
    # remove the end
    if res and self.tag in res:
      self.match_rx = re.compile(r"^\}")
    return res

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
def create_unindenter(walker):
  return _Unindenter(walker)

def create_namespace_remover():
  return _NamespaceRemover()

def update_files(directory):
  timer = TraceTimer()
  timer.start()
  for root, dirs, files in os.walk(directory):
    for name in files:
      file_path = os.path.join(root, name)
      if should_exclude_file(file_path):
        continue
      update_file(file_path, True)
  timer.stop()
  logger.info("Operation took %s seconds", timer.elapsed)

def update_file(file_path, commit_changes=False):
  logger.info("Sanitizing file %s", file_path)
  walker = LineWalker(file_path, commit_changes)
  walker.add_transformer(create_reference_tag_remover())
  walker.add_transformer(create_jshint_remover())
  walker.add_transformer(create_namespace_remover())
  walker.add_transformer(create_unindenter(walker))
  walker.walk()
