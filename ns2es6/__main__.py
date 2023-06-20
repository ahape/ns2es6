import os, sys, shutil, argparse, json
from ns2es6.transforms import (sanitize,
                               create_proper_type_roots,
                               collect_exports,
                               replace_imports,
                               fully_qualify,
                               replace_qualified_with_import)
from ns2es6.utils.logger import get_logger, set_log_level

PROJ_PATH = "/Users/alanhape/Projects/ns2es6"

logger = get_logger(__name__)

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("directory")
  parser.add_argument("--debug", "-v", action="store_true")
  parser.add_argument("--clean", action="store_true")
  return parser.parse_args()

def set_logger_level(args):
  if args.debug:
    set_log_level(logger, "debug")
  else:
    set_log_level(logger, "info")

def clean():
  os.system("git clean -fd")
  os.system("git reset --hard start")

def program(args):
  os.chdir(args.directory)
  if args.clean:
    clean()
  apply_pre_patches()
  create_proper_type_roots.run(args.directory)
  exports = collect_exports.run(args.directory)
  replace_imports.run(args.directory)
  fully_qualify.run(args.directory, exports)
  #open("/tmp/addresses.json", "w").write(json.dumps([str(x) for x in exports]))
  replace_qualified_with_import.run(args.directory, exports)
  sanitize.run(args.directory, True)
  add_globals(args.directory)

def apply_pre_patches():
  # TODO Eventually need to auto-set a "git tag" (and remove on clean())
  for root, _, files in os.walk(os.path.join(PROJ_PATH, "pre")):
    for patch_file in sorted(files):
      full_path = os.path.join(root, patch_file)
      logger.info("Applying patch %s", patch_file)
      os.system(f"git apply --whitespace=fix {full_path}")
      os.system(f'git commit --quiet -am "{patch_file}"')

def add_globals(directory):
  file = "global.d.ts"
  shutil.copyfile(os.path.join(PROJ_PATH, f"post/{file}"),
                  os.path.join(directory, f"ts/{file}"))

def undo_git_changes():
  clean()

def main():
  args = parse_args()
  set_logger_level(args)
  try:
    program(args)
  except:
    undo_git_changes()
    raise

if __name__ == "__main__":
  main()
