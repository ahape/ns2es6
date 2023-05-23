import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import TraceTimer
import ns2es6.utils.helpers as helpers

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
    super().__init__(helpers.Regex.namespace, f"<DELETE>{self.tag}")

  def analyze(self, text):
    res = super().analyze(text)
    # If we are going to remove the namespace start, then we have to also
    # remove the end
    if res and self.tag in res:
      self.match_rx = re.compile(r"^\}")
    return res

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

def update_files(directory, commit_changes=False):
  timer = TraceTimer()
  timer.start()

  helpers.for_each_file(directory, lambda f: update_file(f, commit_changes))

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
