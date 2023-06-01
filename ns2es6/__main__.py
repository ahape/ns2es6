import os, sys, argparse, logging
from ns2es6.transforms import (sanitize,
                               collect_exports,
                               replace_imports,
                               fully_qualify)
from ns2es6.utils.logger import logger

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("directory")
  parser.add_argument("--debug", "-v", action="store_true")
  parser.add_argument("--clean", action="store_true")
  return parser.parse_args()

def set_logger_level(args):
  if args.debug:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)

def program(args):
  os.chdir(f"{args.directory}")
  if args.clean:
    os.system("git reset --hard start")

  apply_pre_patches(args)
  exports = collect_exports.run(args.directory)
  replace_imports.run(args.directory)
  fully_qualify.run(args.directory, exports)
  sanitize.run(args.directory, True)

def apply_pre_patches(args):
  # TODO Eventually need to set a "git tag"
  for root, _, files in os.walk("/Users/alanhape/Projects/ns2es6/pre"):
    for patch_file in sorted(files):
      full_path = os.path.join(root, patch_file)
      os.system(f"git apply --whitespace=fix {full_path}")
      os.system(f'git commit -am "{patch_file}"')

def undo_git_changes(args):
  # TODO should undo until the "git tag" we set if anything fails
  ...

def main():
  args = parse_args()
  set_logger_level(args)
  program(args)

if __name__ == "__main__":
  main()
