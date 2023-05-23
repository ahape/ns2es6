#!/opt/homebrew/bin/python3.11
import os, tempfile
from ns2es6.transforms import sanitize
from ns2es6.utils.line_walker import LineWalker

def test(name, expectation_file, assertion_file):
  expectation = assertion = None
  with open(assertion_file, "r", encoding="utf8") as f:
    assertion = f.read()
  with open(expectation_file, "r", encoding="utf8") as f:
    expectation = f.read()
  try:
    assert expectation == assertion, f"diff {expectation_file} {assertion_file}"
  except AssertionError as ex:
    print(f"Test {name} FAILED. Running diff to see comparison")
    print(f"git diff --no-index {expectation_file} {assertion_file}")
    os.system(f"git diff --no-index {expectation_file} {assertion_file}")
    raise ex

def test_sanitize_01():
  subject_file = "tests/sanitize.ts"
  assertion_file = tempfile.mkstemp()[1]
  expectation_file = "tests/expectations/sanitize.ts"
  walker = LineWalker(subject_file, assertion_file)
  walker.add_transformer(sanitize.create_reference_tag_remover())
  walker.add_transformer(sanitize.create_jshint_remover())
  walker.add_transformer(sanitize.create_namespace_remover())
  walker.add_transformer(sanitize.create_unindenter(walker))
  walker.walk()
  test("sanitize", expectation_file, assertion_file)

test_sanitize_01()

print("All tests passed!")
