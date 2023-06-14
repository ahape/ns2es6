import os, re
from string import Template
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import trace
from ns2es6.utils.symbol import Symbol
from ns2es6.utils import helpers
from ns2es6.transforms.collect_exports import NamespaceCollector

import_template = Template('import { $vars } from "$path";\n')
sub_import_template = Template('const { $vars } = $obj;\n')

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
        text = re.sub(r"\b" + re.escape(symbol.address) + r"\b", symbol.alias, text)
    return text

def process_imports(file_path, imports):
  imports_for_file = {}
  symbols_needing_alias = set()
  # Some symbol replacements were false-positives
  undos = set()
  for symbol in list(imports):
    if os.path.normpath(file_path) == os.path.normpath(symbol.file):
      undos.add(symbol)
      continue

    file_path_dir = os.path.split(file_path)[0]
    symbol_dir, symbol_file = os.path.split(symbol.file)
    rel_dir = os.path.relpath(symbol_dir, file_path_dir)
    rel_path = os.path.join(rel_dir, symbol_file)

    if rel_path not in imports_for_file:
      imports_for_file[rel_path] = set()

    imports_for_file[rel_path].add(symbol)
    symbols_needing_alias.add(symbol)

  write_imports(file_path,
                imports_for_file,
                symbols_needing_alias,
                undos)

def write_imports(file_path, imports_for_file, symbols_needing_alias, undos):
  contents = ""
  with open(file_path, "r", encoding="utf8") as file:
    contents = file.read()
    for undo in undos:
      contents = contents.replace(undo.alias, undo.symbol)
    for rel_path, symbols in imports_for_file.items():
      items = []
      sub_items = {}
      for symbol in symbols:
        symbol_name = symbol.symbol_for_import
        if symbol in symbols_needing_alias:
          if symbol.nested:
            sub_items[symbol_name] = sub_items.get(symbol_name, []) + [symbol.symbol]
          else:
            symbol_name += " as " + symbol.alias
        items.append(symbol_name)
      path_without_ext = rel_path[:-3]
      #unshift> const { SubFoo } = Foo;
      for imp, items in sub_items.items():
        contents = sub_import_template.substitute(vars=", ".join(items),
                                                  obj=imp) + contents
      #unshift> import { Foo } from "xyz"
      contents = import_template.substitute(vars=", ".join(items),
                                            path=path_without_ext) + contents
  with open(file_path, "w", encoding="utf8") as file:
    file.write(contents)

@trace("replace qualified with import")
def run(directory, exports):
  symbols_rx = helpers.create_or_matcher([*map(lambda x: x.address, exports)])
  helpers.for_each_file(directory,
    lambda f: update_file(f, exports, symbols_rx, True))

def update_file(file_path, exports, symbols_rx, commit_changes=False):
  walker = LineWalker(file_path, commit_changes)
  ns_collector = NamespaceCollector()
  walker.add_transformer(ns_collector)
  q_replacer = QualifiedReplacer(symbols_rx, ns_collector, exports)
  walker.add_transformer(q_replacer)
  walker.walk()
  process_imports(file_path, q_replacer.imports)
