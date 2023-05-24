import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import TraceTimer
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
  last_namespace = None

  def __init__(self):
    super().__init__(r"^\s*(?:export\s+){0,1}namespace\s+(\S+)[ {]")
    self.ns_stack = []
    self.col_stack = []

  @property
  def current(self):
    return ".".join(self.ns_stack)

  def analyze(self, text):
    if m := re.search(r"^\s*\}", text):
      # NOTE This isn't robust enough to handle poorly formatted code
      if self.col_stack and text.index("}") <= self.col_stack[-1]:
        self.col_stack.pop()
        self.ns_stack.pop()
    return super().analyze(text)

  def handle_match(self, capture, match):
    self.ns_stack.append(capture)
    text = match.string
    # could be "export" or could be "namespace"
    self.col_stack.append(re.search(r"\b\w+\b", text).start())
    NamespaceCollector.last_namespace = self.current

class ExportCollector(Transformer):
  def __init__(self):
    super().__init__(fr"^\s*export\s+(?:(?:{_keywords})\s+)+(\w+)\b")
    self.exports = set()

  def handle_match(self, capture, match):
    # TODO: Make these proper objects
    last_ns = NamespaceCollector.last_namespace
    # If the export is a namespace _itself_, avoid dup
    if last_ns.endswith(f".{capture}"):
      self.exports.add(last_ns)
    else:
      self.exports.add(f"{last_ns}.{capture}")

def run(directory):
  timer = TraceTimer()
  timer.start()
  helpers.for_each_file(directory, process_file)
  timer.stop()
  logger.debug("Operation took %s seconds", timer.elapsed)

def process_file(file_path):
  logger.debug("Collecting export data from file %s", file_path)
  walker = LineWalker(file_path)
  walker.add_transformer(NamespaceCollector())
  export_tf = ExportCollector()
  walker.add_transformer(export_tf)
  walker.walk()
  return list(export_tf.exports)
