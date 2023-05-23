import re
from .logger import logger

class LineWalker:
  def __init__(self, file_path, commit_changes=False):
    self.file_path = file_path
    self.commit_changes = commit_changes
    self.out_lines = []
    self.tfs = []
    self.has_changed = False
    self.line = None
    self.tags = set()

  def check_tags_for(self, tag):
    return tag in self.tags

  def add_tags_if_any(self):
    self.tags.update(re.findall("(\<@\w+@\>)", self.line))

  def add_transformer(self, tf):
    self.tfs.append(tf)

  def walk(self):
    logger.debug("Analyzing file: %s", self.file_path)
    with open(self.file_path, "r", encoding="utf8") as file:
      for line in file.readlines():
        self.analyze_line(line)

    if self.has_changed:
      res = "".join(self.out_lines)
      #logger.debug("Result\n\n%s", res)

      if self.commit_changes:
        path = self.file_path
        if isinstance(self.commit_changes, str):
          path = self.commit_changes
        logger.info("Committing changes to %s", path)
        with open(path, "w", encoding="utf8") as file:
          file.write(res)
    else:
      logger.debug("No changes found")

  def analyze_line(self, line):
    self.line = line
    self.run_tfs()
    self.write_result()
    self.add_tags_if_any()

  def write_result(self):
    if "<DELETE>" not in self.line:
      self.out_lines.append(self.line)

  def run_tfs(self):
    for tf in self.tfs:
      if (res := tf.analyze(self.line)) and res != self.line:
        self.has_changed = True
        self.line = res
