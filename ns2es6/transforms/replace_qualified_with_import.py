import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import trace
from ns2es6.utils.symbol import Symbol
from ns2es6.utils import helpers
from ns2es6.transforms.collect_exports import NamespaceCollector

# NOTE: use os.path.relpath(path, start)
class QualifiedReplacer(Transformer):
  def __init__(self, match_rx, ns_collector, exports, file_path):
    super().__init__(match_rx)
    self.ns_collector = ns_collector
    self.exports = exports
    self.file_path = file_path
    self.imports = []

@trace("replace qualified with import")
def run(directory, exports):
  symbols_rx = helpers.create_export_matcher(exports)
  helpers.for_each_file(directory,
    lambda f: update_file(f, exports, symbols_rx))

def update_file(file_path, exports, symbols_rx):
  walker = LineWalker(file_path, True)
  ns_collector = NamespaceCollector()
  walker.add_transformer(ns_collector)
  walker.add_transformer(QualifiedReplacer(
    symbols_rx,
    ns_collector,
    exports,
    file_path))
  walker.walk()
