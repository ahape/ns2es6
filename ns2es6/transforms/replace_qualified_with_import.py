import os, re
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import trace
from ns2es6.utils.symbol import Symbol
from ns2es6.utils import helpers
from ns2es6.transforms.collect_exports import NamespaceCollector

class QualifiedReplacer(Transformer):
  def __init__(self, match_rx, ns_collector, exports):
    super().__init__(match_rx)
    self.ns_collector = ns_collector
    self.exports = exports
    self.imports = set()

  def analyze(self, text):
    for match in self.match_rx.finditer(text):
      found = [s for s in self.exports if s.address == match[0]]
      if found and (symbol := found[0]):
        self.imports.add(symbol)
        text = re.sub(r"\b" + re.escape(symbol.address) + r"\b", symbol.symbol, text)
    return text

def add_imports_to_file(file_path, imports):
  imports_for_file = {}
  all_symbol_names, symbols_needing_alias = [], set()
  for symbol in list(imports):
    if file_path == symbol.file:
      continue
    file_path_dir = os.path.split(file_path)[0]
    symbol_dir, symbol_file = os.path.split(symbol.file)
    rel_dir = os.path.relpath(symbol_dir, file_path_dir)
    rel_path = os.path.join(rel_dir, symbol_file)
    if rel_path not in imports_for_file:
      imports_for_file[rel_path] = set()
    if symbol not in imports_for_file[rel_path]:
      imports_for_file[rel_path].add(symbol)
      symbol_name = symbol.symbol
      if symbol_name in all_symbol_names:
        symbols_needing_alias.add(symbol)
      else:
        all_symbol_names.append(symbol_name)
  contents = ""
  with open(file_path, "r", encoding="utf8") as file:
    contents = file.read()
    for rel_path, symbols in imports_for_file.items():
      items = []
      for symbol in symbols:
        symbol_name = symbol.symbol
        if symbol_name in symbols_needing_alias:
          symbol_name += " as " + symbol.alias
        items.append(symbol_name)
      contents = f'import {{ { ", ".join(items) } }} from "{rel_path}";\n' + contents
  with open(file_path, "w", encoding="utf8") as file:
    file.write(contents)

@trace("replace qualified with import")
def run(directory, exports):
  symbols_rx = helpers.create_or_matcher([*map(lambda x: x.address, exports)])
  helpers.for_each_file(directory,
    lambda f: update_file(f, exports, symbols_rx))

def update_file(file_path, exports, symbols_rx):
  walker = LineWalker(file_path, True)
  ns_collector = NamespaceCollector()
  walker.add_transformer(ns_collector)
  q_replacer = QualifiedReplacer(symbols_rx, ns_collector, exports)
  walker.add_transformer(q_replacer)
  walker.walk()
  add_imports_to_file(file_path, q_replacer.imports)
