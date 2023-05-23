import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import TraceTimer
import ns2es6.utils.helpers as helpers

recent_nss = []

class _NamespaceCollector(Transformer):
  match_rx = re.compile(helpers.Regex.namespace)

  def handle_match(self, match):
    recent_nss.append(match)

class _ExportCollector(Transformer):
  def __init__(self):
    super().__init__(helpers.Regex.export)
    self.exports = []

  def handle_match(self, name):
    # TODO: Make these proper objects
    self.exports.append(f"{recent_nss[-1]}.{name}")

def create_namespace_collector():
  return _NamespaceCollector()

def create_export_collector():
  return _ExportCollector()

def run_for_directory(directory):
  timer = TraceTimer()
  timer.start()
  helpers.for_each_file(directory, collect)
  timer.stop()
  logger.debug("Operation took %s seconds", timer.elapsed)

def collect(file_path):
  logger.debug("Collecting export data from file %s", file_path)
  walker = LineWalker(file_path)
  walker.add_transformer(create_namespace_collector())
  export_tf = create_export_collector()
  walker.add_transformer(export_tf)
  walker.walk()
  return export_tf.exports
