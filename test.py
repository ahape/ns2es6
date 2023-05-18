#!/opt/homebrew/bin/python3.11
from ns2es6.transforms import sanitize

sanitize.remove_all_comments("tests/sanitize.ts")
