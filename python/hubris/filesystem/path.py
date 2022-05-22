# Pretty much just exposes the Path type
from pathlib import Path

class InvalidFileTypeException(Exception): ...


def is_empty(path : Path) -> bool :
	"""
	If path is a directory, checks if there are no files within.
	If path is a file, checks if the file size is 0.
	Otherwise raises an InvalidFileTypeException 
	"""

	if path.is_dir():
		for v in path.iterdir():
			return False
		return True

	elif path.is_file():
		sr = path.stat()
		return sr.st_size == 0

	else:
		raise InvalidFileTypeException


