import os, re
from string import Template
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import get_logger
from ns2es6.utils.trace_timer import trace
from ns2es6.utils.symbol import Symbol
from ns2es6.utils import helpers
from ns2es6.transforms.collect_exports import NamespaceCollector

import_template = Template('import { $props } from "$path";')
sub_import_template = Template('const $var = $imported_var.$prop;')

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

def symbols_from_same_file(file_path, imports):
  false_hits = set()
  for symbol in imports:
    if os.path.normpath(file_path) == os.path.normpath(symbol.file):
      false_hits.add(symbol)
  return false_hits

def process_imports(file_path, imports):
  imports = list(imports)
  imports_for_file = {}
  symbols_needing_alias = set()
  # Some symbol replacements were false-positives
  false_hits = symbols_from_same_file(file_path, imports)
  for symbol in filter(lambda x: x not in false_hits, imports):
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
                false_hits)

def prepend_import_statement(contents, props_set, source_path):
  statement = import_template.substitute(
    props=", ".join(sorted(list(props_set))),
    path=source_path.replace(".ts", ""))
  return statement + "\n" + contents

def prepend_nested_import_statements(contents, nested_props):
  statements = []
  for nested_symbols in nested_props.values():
    for symbol in sorted(nested_symbols, key=str):
      statements.append(
        sub_import_template.substitute(
          var          = symbol.alias,
          imported_var = symbol.symbol_for_import,
          prop         = symbol.symbol))
  statements_txt = "\n".join(sorted(statements))
  return statements_txt + "\n" + contents

def write_imports(file_path, imports_for_file, symbols_needing_alias, false_hits):
  contents = ""
  with open(file_path, "r", encoding="utf8") as file:
    contents = file.read()
    # Sometimes collisions will be found _after_ export collection, here we fix
    # those mistakes
    for undo in false_hits:
      contents = contents.replace(undo.alias, undo.symbol)
    for rel_path, symbols in imports_for_file.items():
      props = set()
      nested_props = {}
      for symbol in symbols:
        symbol_name = symbol.symbol_for_import
        if symbol in symbols_needing_alias:
          if symbol.nested:
            nested_props[symbol_name] = nested_props.get(symbol_name, []) + [symbol]
          else:
            symbol_name += " as " + symbol.alias
        props.add(symbol_name)
      #prepend> const SubFoo1 = Foo.SubFoo1;
      #prepend> const SubFoo2 = Foo.SubFoo2;
      #prepend> ...
      if nested_props:
        contents = prepend_nested_import_statements(contents, nested_props)
      #prepend> import { Foo } from "xyz"
      contents = prepend_import_statement(contents, props, rel_path)

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
