import re
from ns2es6.utils.logger import get_logger

class LineWalker:
  def __init__(self, file_path, commit_changes=False):
    self.file_path = file_path
    self.commit_changes = commit_changes
    self.out_lines = []
    self.tfs = []
    self.has_changed = False
    self.line = None

  def add_transformer(self, tf):
    self.tfs.append(tf)

  def walk(self):
    with open(self.file_path, "r", encoding="utf8") as file:
      for line in file.readlines():
        self.analyze_line(line)

    result = "".join(self.out_lines)

    if self.commit_changes:
      path = self.file_path
      if isinstance(self.commit_changes, str):
        path = self.commit_changes
      with open(path, "w", encoding="utf8") as file:
        file.write(result)

  def analyze_line(self, line):
    self.line = line
    self.run_tfs()
    self.write_result()

  def write_result(self):
    if "<DELETE>" not in self.line:
      self.out_lines.append(self.line)

  def run_tfs(self):
    for tf in self.tfs:
      if (res := tf.analyze(self.line)) and res != self.line:
        self.has_changed = True
        self.line = res
