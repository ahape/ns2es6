import os, sys, argparse, logging
from .transforms import sanitize
from .utils.logger import logger

dir_ = sys.argv[-1]

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("directory")
  parser.add_argument("--debug", "-v", action="store_true")
  return parser.parse_args()

def main(args):
  sanitize.run(args.directory)

if __name__ == "__main__":
  _args = parse_args()
  logger.setLevel(logging.INFO)
  if _args.debug:
    logger.setLevel(logging.DEBUG)
  main(_args)
