import os, sys

def should_exclude_file(file_path):
  return "node_modules" in file_path or \
      not file_path.endswith(".ts") or \
      file_path.endswith(".d.ts")

def for_each_file(directory, callback):
  for root, _, files in os.walk(directory):
    for name in files:
      file_path = os.path.join(root, name)
      if should_exclude_file(file_path):
        continue
      callback(file_path)
