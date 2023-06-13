import os, re, shutil
from ns2es6.utils.transformer import Transformer
from ns2es6.utils.line_walker import LineWalker
from ns2es6.utils.logger import logger
from ns2es6.utils.trace_timer import trace
from ns2es6.utils.symbol import Symbol
from ns2es6.utils import helpers

typename_from_file_rx = re.compile(r"^(\w+(?:-[a-z]+)?).*")

def get_folder_name(file_path):
  print(file_path)
  # need to extract the last part of the file
  return typename_from_file_rx.match(file_path)[0]

def create_type_file(directory, file_path):
  # Create folder for file
  folder = os.path.join(directory, get_folder_name(file_path))
  os.path.makedirs(folder)
  # Move file to foo/index.d.ts
  shutil.move(file_path, os.path.join(folder, "index.d.ts"))

@trace("create proper type roots")
def run(directory):
  types_dir = os.path.join(directory, "types")
  for root, _, files in os.walk(types_dir):
    for name in files:
      file_path = os.path.join(root, name)
      create_type_file(directory, file_path)
