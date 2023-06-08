import os, sys, argparse, logging, json
from ns2es6.transforms import (sanitize,
                               collect_exports,
                               replace_imports,
                               fully_qualify,
                               replace_qualified_with_import)
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

def clean():
  os.system("git clean -fd")
  os.system("git reset --hard start")

def program(args):
  os.chdir(args.directory)
  if args.clean:
    clean()
  apply_pre_patches()
  exports = collect_exports.run(args.directory)
  replace_imports.run(args.directory)
  fully_qualify.run(args.directory, exports)
  #open("/tmp/addresses.json", "w").write(json.dumps([str(x) for x in exports]))
  replace_qualified_with_import.run(args.directory, exports)
  sanitize.run(args.directory, True)
  add_globals(args.directory)

def apply_pre_patches():
  # TODO Eventually need to auto-set a "git tag" (and remove on clean())
  for root, _, files in os.walk("/Users/alanhape/Projects/ns2es6/pre"):
    for patch_file in sorted(files):
      full_path = os.path.join(root, patch_file)
      logger.info(f"Applying patch {patch_file}")
      os.system(f"git apply --whitespace=fix {full_path}")
      os.system(f'git commit --quiet -am "{patch_file}"')

def add_globals(directory):
  with open(os.path.join(directory, "ts", "global.d.ts"), "w", encoding="utf8") as f:
    lines = []
    lines.append("import { IDataSourceGroup } from 'Interfaces/idatasourcegroup';")
    lines.append("declare global {")
    lines.append("  declare const _: _.UnderscoreStatic;")
    lines.append("  declare const dataConnectionGroups: IDataSourceGroup[];")
    lines.append("}")
    f.write("\n".join(lines))

def undo_git_changes(directory):
  clean()

def main():
  args = parse_args()
  set_logger_level(args)
  try:
    program(args)
  except:
    undo_git_changes(args.directory)
    raise

if __name__ == "__main__":
  main()
