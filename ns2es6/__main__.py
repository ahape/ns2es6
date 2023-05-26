import os, sys, argparse, logging
from ns2es6.transforms import (sanitize,
                               collect_exports,
                               replace_imports)
from ns2es6.utils.logger import logger

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("directory")
  parser.add_argument("--debug", "-v", action="store_true")
  return parser.parse_args()

def set_logger_level(args):
  if args.debug:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)

def program(args):
  #sanitize.run(args.directory)
  #collect_exports.run(args.directory)
  apply_pre_patches(args)
  replace_imports.run(args.directory)
  #replace_imports.update_file("tests/replace_imports_02.ts", "tests/expectations/replace_imports_02.ts")

def apply_pre_patches(args):
  # TODO First need to set a "git tag"
  for root, _, files in os.walk("/Users/alanhape/Projects/ns2es6/pre"):
    for patch_file in files:
      full_path = os.path.join(root, patch_file)
      cmd = f"cd {args.directory}"
      cmd += f" && git apply --whitespace=fix {full_path}"
      cmd += f' && git commit -am "{patch_file}"'
      os.system(cmd)

def undo_git_changes(args):
  # TODO should undo until the "git tag" we set if anything fails
  ...

def main():
  args = parse_args()
  set_logger_level(args)

  program(args)

if __name__ == "__main__":
  main()
