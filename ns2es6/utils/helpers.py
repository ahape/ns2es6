import os, sys

_keywords = "|".join([
  "class",
  "namespace",
  "function",
  "type",
  "interface",
  "enum",
  "const",
  "let",
  "abstract",
  "var",
])

class Regex:
  namespace = r"^\s*namespace\s+(\S+)[ {]"
  export = fr"^\s*export\s+(?:(?:{_keywords})\s+)+(\w+)\b"

def should_exclude_file(file_path):
  return "node_modules" in file_path or \
      not file_path.endswith(".ts")

def for_each_file(directory, callback):
  for root, _, files in os.walk(directory):
    for name in files:
      file_path = os.path.join(root, name)
      if should_exclude_file(file_path):
        continue
      callback(file_path)
