import os, re, shutil
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.trace_timer import trace
from ns2es6.utils.symbol import Symbol
from ns2es6.utils import helpers

typename_from_file_rx = re.compile(r"^(\w+(?:-[a-z]+)?).*")

def get_folder_name(file_path):
  file_name = os.path.split(file_path)[1]
  return typename_from_file_rx.match(file_name)[1]

def create_type_file(directory, file_path):
  folder = os.path.join(directory, get_folder_name(file_path))
  # Create folder for file
  os.makedirs(folder)
  # Move file to foo/index.d.ts
  shutil.move(file_path, os.path.join(folder, "index.d.ts"))

@trace("create proper type roots")
def run(directory):
  types_dir = os.path.join(directory, "types")
  for root, _, files in os.walk(types_dir):
    for name in files:
      if name.endswith(".d.ts"):
        file_path = os.path.join(root, name)
        create_type_file(root, file_path)
