#
#	C++ Type utility
#

from .core import InvalidType, TestFailed

import re


class StringSplitter:
	
	class SplitToken:
		def __init__(self, token : str, ignore : bool = False):
			self.token = token
			self.ignore = ignore


	def parse(self, what : str) -> "list[str]":
		parts = []
		cur_part = None
		for c in what:
			found = False
			for split_char in self._split_chars:
				if split_char.token == c:
					if cur_part is not None:
						parts.append(cur_part)
						cur_part = None
					if not split_char.ignore:
						parts.append(split_char.token)
					found = True
					break
			if not found:
				if cur_part is None:
					cur_part = c
				else:
					cur_part += c
		if cur_part is not None:
			parts.append(cur_part)
			cur_part = None
		return parts

	def __init__(self, split_chars : "list[SplitToken]" = [SplitToken(" ")]):
		self._split_chars = split_chars



def _split_type_name(name : str) -> "list[str]":
	splitter = StringSplitter([
		StringSplitter.SplitToken("*", ignore=False),
		StringSplitter.SplitToken("&", ignore=False),
		StringSplitter.SplitToken(" ", ignore=True),
	])
	parts = splitter.parse(name)

	if len(parts) > 1:
		if parts[0] == "const":
			f = parts.pop(0)
			parts.insert(1, f)
		
		remove_indexes = []
		for i in range(len(parts)):
			if i == 0:
				continue
			last_i = i - 1
			if parts[i] == "const" and parts[last_i] == "const":
				remove_indexes.append(i)
		for v in remove_indexes:
			parts.pop(v)

	return parts



class Type:
	""" C++ type.

    Arguments:
      	name: The name of the type.
	"""

	def is_pointer(self) -> bool:
		p = len(self._parts) - 1
		if self.is_const():
			p -= 1
		return self._parts[p] == '*'

	def is_reference(self) -> bool:
		p = len(self._parts) - 1
		if self.is_const():
			p -= 1
		return self._parts[p] == '&'

	def is_const(self) -> bool:
		return self._parts[len(self._parts) - 1] == "const"

	def name(self) -> str:
		return self._name
	def parts(self) -> "list[str]":
		return self._parts
	def root(self) -> str:
		return self._root

	def add_pointer(self):
		if self.is_reference():
			raise InvalidType("Cannot make pointer to reference")
		self._parts.append('*')
	def add_reference(self):
		self._parts.append('&')
	def add_const(self):
		if self.is_reference():
			raise InvalidType("Cannot make const reference")
		if not self.is_const():
			self._parts.append('const')

	def __init__(self, name : str):
		
		# The full name string
		self._name = name

		# The parts of the type
		self._parts = _split_type_name(name)

		# The root name of the type
		self._root = self._parts[0]

	def __str__(self) -> str :
		return " ".join(self._parts)

	def _test_type(name, root, parts, is_pointer, is_reference, is_const, test_name = "test"):
		t = Type(name)
		if t.name() != name:
			raise TestFailed(test_name, f"Type.name() for type '{name}' did not return '{name}', got {t.name()}")
		if t.root() != root:
			raise TestFailed(test_name, f"Type.root() for type '{name}' did not return '{root}', got {t.root()}")
		if t.parts() != parts:
			raise TestFailed(test_name, f"Type.parts() for type '{name}' did not return '{parts}', got {t.parts()}")
		if t.is_pointer() != is_pointer:
			raise TestFailed(test_name, f"Type.is_pointer() for type '{name}' returned {t.is_pointer()} - expected {is_pointer}")
		if t.is_reference() != is_reference:
			raise TestFailed(test_name, f"Type.is_reference() for type '{name}' returned {t.is_reference()} - expected {is_reference}")
		if t.is_const() != is_const:
			raise TestFailed(test_name, f"Type.is_const() for type '{name}' returned {t.is_const()} - expected {is_const}")
		


	def _test_value_type(name):
		Type._test_type(name, root=name, parts=[name], is_pointer=False, is_reference=False, is_const=False,
			test_name="C++ Value Type")
	def _test_pointer_type(root):
		Type._test_type(root + "*", root=root, parts=[root, "*"], is_pointer=True, is_reference=False, is_const=False,
			test_name="C++ Pointer Type")
	def _test_reference_type(root):
		Type._test_type(root + "&", root=root, parts=[root, "&"], is_pointer=False, is_reference=True, is_const=False,
			test_name="C++ Reference Type")

	def _test_const_value_type(name):
		Type._test_type("const " + name, root=name, parts=[name, "const"], is_pointer=False, is_reference=False, is_const=True,
			test_name="C++ Const Value Type - West Const")
		Type._test_type(name + " const", root=name, parts=[name, "const"], is_pointer=False, is_reference=False, is_const=True,
			test_name="C++ Const Value Type - East Const")

	def _test_full_type(name):

		t = Type(name)
		if t.is_const():
			raise TestFailed("C++ Full Type", f"is_const return True - expected False")
		t.add_const()
		if not t.is_const():
			raise TestFailed("C++ Full Type", f"is_const return False - expected True")
		t.add_pointer()
		if not t.is_pointer():
			raise TestFailed("C++ Full Type", f"is_pointer returned False - expected True")
		t.add_const()
		if not t.is_const():
			raise TestFailed("C++ Full Type", f"is_const return False - expected True")
		if not t.is_pointer():
			raise TestFailed("C++ Full Type", f"is_pointer returned False - expected True")
		t.add_reference()

		try:
			t.add_const()
			raise TestFailed("C++ Full Type", f"Adding const to reference type expected InvalidType to be raised")
		except InvalidType:
			pass
		try:
			t.add_pointer()
			raise TestFailed("C++ Full Type", f"Adding pointer to reference type expected InvalidType to be raised")
		except InvalidType:
			pass

	def __test__():
		"""Runs a test to ensure this is implemented correctly"""

		if _split_type_name("int*") != ["int", '*']:
			raise TestFailed("_split_type_name", f'Got {_split_type_name("int*")}')

		Type._test_value_type("int")
		Type._test_value_type("float")
		Type._test_value_type("double")

		Type._test_pointer_type("int")
		Type._test_pointer_type("float")
		Type._test_pointer_type("double")

		Type._test_reference_type("int")
		Type._test_reference_type("float")
		Type._test_reference_type("double")
		
		Type._test_const_value_type("int")
		Type._test_const_value_type("float")
		Type._test_const_value_type("double")

		Type._test_full_type("int")
		Type._test_full_type("float")
		Type._test_full_type("double")



