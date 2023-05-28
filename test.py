#!/opt/homebrew/bin/python3.11
import os, tempfile, json
from ns2es6.transforms import (sanitize,
                               collect_exports,
                               replace_imports)
from ns2es6.utils.line_walker import LineWalker

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

#test_sanitize(1)
test_collect_exports(6)
test_replace_imports(3)

print("All tests passed!")
