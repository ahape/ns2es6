#!/opt/homebrew/bin/python3.11
import os, hashlib
from ns2es6.transforms import sanitize

tempfile = "tmp"
sanitize.remove_all_comments("tests/sanitize.ts", tempfile)
output = open(tempfile).read()
assert hashlib(output) == ..., # TODO

