from pathlib import Path
import re




def count_lines_in_dir(dir : Path, countLinesFn, recursive : bool, depth : int = 0):
	n = 0
	for p in dir.iterdir():
		if p.is_dir():
			if recursive or (depth < 1):
				n += count_lines_in_dir(p, countLinesFn, recursive=recursive, depth=depth + 1)
		else:
			if p.suffix == ".cpp" or p.suffix == ".hpp":
				n += countLinesFn(p)
	return n


def make_count_fn(productiveLinesOnly : bool, match : str | None):

	_matchPattern = None
	if match is not None:
		_matchPattern = re.compile(match)

	if productiveLinesOnly:
		def _myfn(p : Path) -> int :
			if match is not None:
				if not _matchPattern.search(str(p)):
					return 0
			n = 0
			ls = open(p, "r").read().splitlines(False)
			for v in ls:
				if len(v) != 0 and len(v.strip()) != 0:
					n += 1
			return n
		return _myfn
	else:
		def _myfn(p : Path) -> int :
			if match is not None:
				if not _matchPattern.search(str(p)):
					return 0
			ls = open(p, "r").readlines()
			return len(ls)
		return _myfn


def count_lines(directories : "list[Path]",
	productiveLinesOnly : bool = False,
	match : str | None = None,
	recursive : bool = False
):
	countFn = make_count_fn(
		productiveLinesOnly = productiveLinesOnly,
		match = match
	)	

	n = 0
	for v in directories:
		n += count_lines_in_dir(Path(v),
			countLinesFn = countFn,
			recursive = recursive,
			depth = 0)
	
	return n
