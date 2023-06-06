#!/opt/homebrew/bin/python3.11
import os, tempfile, json
from ns2es6.transforms import (sanitize,
                               collect_exports,
                               replace_imports,
                               fully_qualify)
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.symbol import Symbol
import ns2es6.utils.helpers as helpers

def read_file(file_path):
  with open(file_path, "r", encoding="utf8") as f:
    return f.read()

def read_file_as_json(file_path):
  with open(file_path, "r", encoding="utf8") as f:
    return json.load(f)

def assert_files_are_same(test_name, expectation_file, assertion_file):
  expectation = read_file(expectation_file)
  assertion = read_file(assertion_file)
  try:
    assert expectation == assertion, f"diff {expectation_file} {assertion_file}"
  except AssertionError as ex:
    print(f"Test {test_name} FAILED. Running diff to see comparison")
    print(f"git diff --no-index {expectation_file} {assertion_file}")
    os.system(f"git diff --no-index {expectation_file} {assertion_file}")
    raise ex

def test_sanitize(file_count):
  for i in range(1, file_count + 1):
    subject_file = f"tests/sanitize_{str(i).zfill(2)}.ts"
    expectation_file = f"tests/expectations/sanitize_{str(i).zfill(2)}.ts"
    assertion_file = tempfile.mkstemp()[1]
    sanitize.update_file(subject_file, assertion_file)
    assert_files_are_same("sanitize", expectation_file, assertion_file)

def test_collect_exports(file_count, only=None):
  for i in range(1, file_count + 1):
    if not only or i == only:
      subject_file = f"tests/collect_exports_{str(i).zfill(2)}.ts"
      expectation_file = f"tests/expectations/collect_exports_{str(i).zfill(2)}.json"
      assertion = sorted(map(str, collect_exports.process_file(subject_file)))
      expectation = sorted(map(str, read_file_as_json(expectation_file)))
      for i, e in enumerate(expectation):
        assert e == assertion[i], (e, assertion[i])

def test_replace_imports(file_count):
  for i in range(1, file_count + 1):
    subject_file = f"tests/replace_imports_{str(i).zfill(2)}.ts"
    expectation_file = f"tests/expectations/replace_imports_{str(i).zfill(2)}.ts"
    assertion_file = tempfile.mkstemp()[1]
    replace_imports.update_file(subject_file, assertion_file)
    assert_files_are_same("replace_imports", expectation_file, assertion_file)

def test_fully_qualify(file_count):
  for i in range(1, file_count + 1):
    num = str(i).zfill(2)
    subject_file = f"tests/fully_qualify_{num}.ts"
    expectation_file = f"tests/expectations/fully_qualify_{num}.ts"
    exports = []
    with open(f"tests/fully_qualify_{num}.json", "r", encoding="utf8") as f:
      exports = json.loads(f.read())
    exports = [Symbol(x["symbol"], x["ns"], x["file"]) for x in exports]
    symbols_rx = helpers.create_or_matcher([*map(lambda x: x.symbol, exports)])
    assertion_file = tempfile.mkstemp()[1]
    fully_qualify.update_file(subject_file, exports, symbols_rx, assertion_file)
    assert_files_are_same("fully qualify", expectation_file, assertion_file)

#test_sanitize(1)
test_collect_exports(6)
test_replace_imports(3)
test_fully_qualify(1)

print("All tests passed!")
