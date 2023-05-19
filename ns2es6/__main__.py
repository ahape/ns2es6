import os, sys, argparse, logging
from .transforms import sanitize
from .utils.logger import logger

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("directory")
  parser.add_argument("--debug", "-v", action="store_true")
  return parser.parse_args()

def set_logger_level(args):
  if _args.debug:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)

def main(args):
  sanitize.run(args.directory)

if __name__ == "__main__":
  _args = parse_args()
  set_logger_level(_args)
  main(_args)
