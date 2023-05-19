#!/opt/homebrew/bin/python3.11
import os, hashlib, tempfile
from ns2es6.transforms import sanitize

def hexify(text):
  m = hashlib.sha256()
  m.update(text.encode("utf8"))
  return m.hexdigest()

_, path = tempfile.mkstemp()

# Test sanitize
sanitize.remove_all_comments("tests/sanitize.ts", path)
output = open(path).read()
assert hexify(output) == "7a69bc8d974476a79a7e2f2c21a621c5ffddba105636203bcc05e4bec4833d20", output

print("All tests passed!")
