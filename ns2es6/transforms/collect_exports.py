import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import TraceTimer
from ns2es6.utils.symbol import Symbol
from ns2es6.utils import helpers

_keywords = "|".join([
  "class",
  "namespace",
  "function",
  "type",
  "interface",
  "enum",
  "const",
  "let",
  "abstract",
  "var",
])

class NamespaceCollector(Transformer):
  def __init__(self):
    super().__init__(r"^\s*(?:export\s+){0,1}namespace\s+(\S+)[ {]")
    self.ns_stack = []
    self.col_stack = []

  @property
  def current(self):
    return ".".join(self.ns_stack)

  def analyze(self, text):
    if re.search(r"^\s*\}", text):
      # NOTE This isn't robust enough to handle poorly formatted code
      if self.col_stack and text.index("}") <= self.col_stack[-1]:
        self.col_stack.pop()
        self.ns_stack.pop()
    return super().analyze(text)

  def handle_match(self, capture, match):
    self.ns_stack.append(capture)
    text = match.string
    # could be "export" (from export namespace) or could be "namespace"
    self.col_stack.append(re.search(r"\b\w+\b", text).start())

class ExportCollector(Transformer):
  def __init__(self, ns_collector, file_path):
    super().__init__(fr"^\s*export\s+(?:(?:{_keywords})\s+)+(\w+)\b")
    self.exports = set()
    self.file_path = file_path
    self.ns_collector = ns_collector

  def handle_match(self, capture, match):
    # xTODO: Make these proper objects
    current_ns = self.ns_collector.current
    # If the export is a namespace _itself_, avoid dup
    if current_ns and current_ns.endswith(f".{capture}"):
      current_ns = current_ns.replace(f".{capture}", "")
    self.exports.add(Symbol(capture, current_ns, self.file_path))

def run(directory):
  exports = []

  def file_fn(file_path):
    nonlocal exports
    exports += process_file(file_path)

  timer = TraceTimer()
  timer.start()
  helpers.for_each_file(directory, file_fn)
  timer.stop()
  logger.debug("Operation took %s seconds", timer.elapsed)
  return exports

def process_file(file_path):
  logger.debug("Collecting export data from file %s", file_path)
  walker = LineWalker(file_path)
  ns_collector = NamespaceCollector()
  walker.add_transformer(ns_collector)
  export_tf = ExportCollector(ns_collector, file_path)
  walker.add_transformer(export_tf)
  walker.walk()
  return export_tf.exports
