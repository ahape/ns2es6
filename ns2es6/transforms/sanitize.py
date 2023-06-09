import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import get_logger
from ns2es6.utils.trace_timer import trace
from ns2es6.utils import helpers

ns_start_rx = r"^namespace\s+(\S+)[ {]"
ns_end_rx = r"^\}"


# Unindent everything 1x. Since everything will be reduced by one block scope
# (the namespace block that will be removed) this will make subsequent
# changes easier to grok
class Unindenter(Transformer):
  def __init__(self):
    super().__init__(r"^\s{4}", "")
    self.in_namespace = False

  def analyze(self, text):
    if not self.in_namespace and re.search(ns_start_rx, text):
      self.in_namespace = True
    if self.in_namespace and re.search(ns_end_rx, text):
      self.in_namespace = False
    return super().analyze(text)

class NamespaceRemover(Transformer):
  def __init__(self):
    super().__init__(ns_start_rx, "<DELETE>")
    self.in_namespace = False

  def analyze(self, text):
    if not self.in_namespace and re.search(ns_start_rx, text):
      self.in_namespace = True
      self.match_rx = re.compile(ns_start_rx)
    if self.in_namespace and re.search(ns_end_rx, text):
      self.in_namespace = False
      self.match_rx = re.compile(ns_end_rx)
    return super().analyze(text)

@trace("sanitize")
def run(directory, commit_changes=False):
  helpers.for_each_file(directory, lambda f: update_file(f, commit_changes))

def update_file(file_path, commit_changes=False):
  walker = LineWalker(file_path, commit_changes)
  walker.add_transformer(Transformer(r"\/\/\/\s*\<reference ", "<DELETE>"))
  walker.add_transformer(Transformer(r"\bjshint\b", "<DELETE>"))
  walker.add_transformer(NamespaceRemover())
  walker.add_transformer(Unindenter())
  walker.walk()
