from collections.abc import Generator
import shutil

from .path import Path


class _DirectoryIterator:
	def __iter__(self):
		self._it = self._dir.iterdir()
		return self
	def __next__(self):
		return next(self._it)
	def __init__(self, path : "str | Path") :
		self._dir = Path(path)
		self._it = self._dir.iterdir()




class _DRecIterStackVal:
	def __iter__(self):
		self.it.__iter__()
		return self
	def __next__(self):
		return self.it.__next__()
	def __init__(self, _path : Path, _parent : "_DRecIterStackVal | None" = None):
		if _parent is not None and not _path.is_absolute() and not _path.is_symlink():
			self.path = _parent.path.joinpath(_path)
		else:
			self.path = _path

		self.parent = _parent
		self.it = self.path.iterdir()

class _DirectoryIteratorRecursive:

	def _pop(self) :
		if len(self._stack) != 0:
			self._stack.pop()

	def _push(self, dir : "Path") :
		self._stack.append( _DRecIterStackVal(dir, self._stack[0] ))

	def _next(self) -> Path :

		# Stop iterating when we have finished the entire stack
		if len(self._stack) == 0:
			raise StopIteration()

		# Grab the current iterator
		_curIt = self._stack[-1]
		try:

			# Look and look and look
			_curVal = None
			while True:
				# Try to iterate
				_curVal = next(_curIt)

				# If an ignore function is set, invoke it
				if (self._ignoreFn is not None) and self._ignoreFn(_curVal):
					# Keep looking
					continue
				else:
					_keepLooking = False
					break

			print(str(_curVal))

			if self._followSymlinks and _curVal.is_symlink():
				# Follow symlink if enabled
				_symTarget = _curVal.resolve(strict = True)
				self._push(_symTarget)
			
			elif _curVal.is_dir():
				# Iterate into directory
				self._push(_curVal)

			# Return the path we just recieved, relative to the starting directory						 
			return _curIt.path.joinpath(_curVal) 

		except StopIteration:
			# Return to the previous directory iterator
			self._pop()

			# Recurse back into this function, now returned to the parent directory
			return self._next()


	def __iter__(self):
		self._stack : "list[_DRecIterStackVal]" = [ _DRecIterStackVal(self._startDir) ]
		return self

	def __next__(self):
		return self._next()

	def __init__(self, path : "str | Path", follow_symlinks : bool = False, ignoreFn : "function(Path) | None" = None) :
		self._startDir = Path(path)
		self._followSymlinks = follow_symlinks
		self._ignoreFn = ignoreFn
		self._stack : "list[_DRecIterStackVal]" = [ _DRecIterStackVal(self._startDir) ]
	
class DirectoryIterator:
	def __iter__(self):
		return self._iter.__iter__()
	def __next__(self):
		return self._iter.__next__()
	def __init__(self, path : "str | Path", recursive : bool = False,  follow_symlinks : bool = False,
		ignoreFn : "function(Path) | None" = None) :
		
		if recursive:
			self._iter = _DirectoryIteratorRecursive(path, follow_symlinks, ignoreFn=ignoreFn)
		else:
			self._iter = _DirectoryIterator(path)


def list_children(path : "str | Path", recursive : bool = False, follow_symlinks : bool = False):
	o : "list[Path]" = []
	for v in DirectoryIterator(path, recursive=recursive, follow_symlinks=follow_symlinks):
		o.append(v)
	return o


def fn_not(fn) :
	def _fn(*args):
		return not fn(*args)
	return _fn

def filter_children(path : "str | Path", filterFn : "function(Path)",
	recursive : bool = False, follow_symlinks : bool = False, ignoreFn : "function(Path) | None" = None):
	o : "list[Path]" = []
	for v in DirectoryIterator(path, recursive=recursive,
		follow_symlinks=follow_symlinks, ignoreFn = ignoreFn):
		if filterFn(v):
			o.append(v)
	return o




def count_directory_contents(path : "str | Path") -> int:
	"""
	Counts the number of files within a directory.
	Defaults to non-recursive. 
	"""
	n = 0
	for v in path.iterdir():
		n += 1
	return n
