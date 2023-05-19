from ..utils.transformer import Transformer
from ..utils.line_walker import LineWalker

class _LineRemover(Transformer):
  def __init__(self, match_rx):
    super().__init__(match_rx, "<DELETE>")

def remove_all_comments(file_path, commit_changes=False):
  reference_remover = _LineRemover(r"\/\/\/\s*\<reference ")
  jshint_remover = _LineRemover(r"\bjshint\b")
  tslint_remover = _LineRemover(r"\btslint\b")

  walker = LineWalker(file_path, commit_changes)
  walker.add_transformer(reference_remover)
  walker.add_transformer(jshint_remover)
  walker.add_transformer(tslint_remover)
  walker.walk()
