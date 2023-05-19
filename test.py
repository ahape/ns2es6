#!/opt/homebrew/bin/python3.11
import os, tempfile
from ns2es6.transforms import sanitize
from ns2es6.utils.line_walker import LineWalker

def test(name, expectation_file, assertion_file):
  assertion = open(assertion_file).read()
  expectation = open(expectation_file).read()
  try:
    assert expectation == assertion, f"diff {expectation_file} {assertion_file}"
  except AssertionError:
    print(f"Test {name} FAILED. Running diff to see comparison")
    print(f"git diff --no-index {expectation_file} {assertion_file}")
    os.system(f"git diff --no-index {expectation_file} {assertion_file}")
    raise SystemExit

def test_sanitize():
  subject_file = "tests/sanitize.ts"
  assertion_file = tempfile.mkstemp()[1]
  expectation_file = "tests/expectations/sanitize.ts"
  walker = LineWalker(subject_file, assertion_file)
  walker.add_transformer(sanitize.create_reference_tag_remover())
  walker.add_transformer(sanitize.create_jshint_remover())
  walker.add_transformer(sanitize.create_unindenter())
  walker.add_transformer(sanitize.create_namespace_remover())
  walker.walk()
  test("sanitize", expectation_file, assertion_file)

test_sanitize()

print("All tests passed!")
