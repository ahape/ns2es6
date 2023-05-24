import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import TraceTimer
from ns2es6.utils import helpers

recent_nss = []

class NamespaceCollector(Transformer):
  def __init__(self):
    super().__init__(helpers.Regex.namespace)

  def handle_match(self, match):
    recent_nss.append(match)

class ExportCollector(Transformer):
  def __init__(self):
    super().__init__(helpers.Regex.export)
    self.exports = []

  def handle_match(self, match):
    # TODO: Make these proper objects
    self.exports.append(f"{recent_nss[-1]}.{match}")

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
  return export_tf.exports
