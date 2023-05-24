#!/opt/homebrew/bin/python3.11
import os, tempfile, json
from ns2es6.transforms import sanitize, collect_exports
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

def test_sanitize_01():
  subject_file = "tests/sanitize.ts"
  assertion_file = tempfile.mkstemp()[1]
  expectation_file = "tests/expectations/sanitize.ts"
  sanitize.update_file(subject_file, assertion_file)
  assert_files_are_same("sanitize", expectation_file, assertion_file)

def test_collect_exports_01():
  subject_file = "tests/collect_exports_01.ts"
  expectation_file = "tests/expectations/collect_exports_01.json"
  assertion = sorted(collect_exports.process_file(subject_file))
  expectation = sorted(read_file_as_json(expectation_file))
  for i, e in enumerate(expectation):
    assert e == assertion[i], (e, assertion[i])

def test_collect_exports_02():
  subject_file = "tests/collect_exports_02.ts"
  expectation_file = "tests/expectations/collect_exports_02.json"
  assertion = sorted(collect_exports.process_file(subject_file))
  expectation = sorted(read_file_as_json(expectation_file))
  for i, e in enumerate(expectation):
    assert e == assertion[i], (e, assertion[i])

test_sanitize_01()
test_collect_exports_01()
test_collect_exports_02()

print("All tests passed!")
