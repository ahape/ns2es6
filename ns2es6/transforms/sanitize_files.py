from ..utils import Transformer, LineWalker

class _LineRemover(Transformer):
  def __init__(self, match_rx, replacement="<DELETE>"):
    super().__init__(match_rx, replacement)

def remove_all_comments(file_path):
  reference_remover = _LineRemover(replace=r"\/\/\/\s*\<reference ")
  jshint_remover = _LineRemover(replace=r"\bjshint\b")
  tslint_remover = _LineRemover(replace=r"\btslint\b")

  walker = LineWalker(file_path)
  walker.add_transformer(reference_remover)
  walker.add_transformer(jshint_remover)
  walker.add_transformer(tslint_remover)
  walker.walk()
