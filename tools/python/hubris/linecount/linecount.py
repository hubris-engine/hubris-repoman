from pathlib import Path




def count_lines_in_dir(dir : Path, countLinesFn):
	n = 0
	for p in dir.iterdir():
		if p.is_dir():
			n += count_lines_in_dir(p, countLinesFn)
		else:
			if p.suffix == ".cpp" or p.suffix == ".hpp":
				n += countLinesFn(p)
	return n


def make_count_fn(productiveLinesOnly : bool):
	if productiveLinesOnly:
		def _myfn(p : Path) -> int :
			n = 0
			ls = open(p, "r").read().splitlines(False)
			for v in ls:
				if len(v) != 0 and len(v.strip()) != 0:
					n += 1
			return n
		return _myfn
	else:
		def _myfn(p : Path) -> int :
			ls = open(p, "r").readlines()
			return len(ls)
		return _myfn


def count_lines(directories : "list[Path]",
	productiveLinesOnly : bool = False):
	countFn = make_count_fn(
		productiveLinesOnly=productiveLinesOnly
	)	

	n = 0
	for v in directories:
		n += count_lines_in_dir(Path(v), countLinesFn=countFn)
	
	return n
