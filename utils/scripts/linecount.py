import hubris.linecount as lc

from argparse import ArgumentParser
from pathlib import Path

parser = ArgumentParser()
parser.add_argument("paths", type=Path, nargs="+", help="The files to count lines on. If these are directories their contents are searched.")
parser.add_argument("--productive_only", "-p", action="store_true", help="Causes only productive lines to be counted.")
parser.add_argument("--match", type=str, default=None, help="Optional pattern that can be specified that file paths must match to be counted.")
parser.add_argument("--recursive", "-r", action="store_true", help="Causes directories to be searched recursive.")

args = parser.parse_args()

productive_only = args.productive_only
paths = args.paths
match = args.match
recursive = args.recursive

n = lc.count_lines(paths, productiveLinesOnly=productive_only, recursive=recursive, match=match)
print(n)
