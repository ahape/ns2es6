from .logger import logger

class LineWalker:
  file_path = None
  tfs = []
  has_changed = False
  line = None
  out_lines = []

  def __init__(self, file_path, commit_changes=False):
    self.file = file_path
    self.commit_changes = commit_changes

  def add_transformer(self, tf):
    self.tfs.append(tf)

  def walk(self):
    with open(self.file_path, "r", encoding="utf8") as file:
      for line in self.file.readlines():
        self.analyze_line(line)

    if self.has_changed:
      res = "".join(self.out_lines)
      logger.debug("Result\n\n%s", res)

      if self.commit_changes:
        logger.debug("Committing changes")
        with open(self.file_path, "w", encoding="utf8") as file:
            file.write(res)

  def analyze_line(self, line):
    self.line = line
    self.run_tfs()
    self.write_result()

  def write_result(self):
    if self.line != "<DELETE>":
      self.out_lines.append(self.line)

  def run_tfs(self):
    for tf in self.tfs:
      if (res := tf.analyze(self.line)) and res != self.line:
        self.has_changed = True
        self.line = res
