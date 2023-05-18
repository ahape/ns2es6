#!/opt/homebrew/bin/python3.11
from .transforms.sanitize_files import CommentRemover


print(CommentRemover("a"))
