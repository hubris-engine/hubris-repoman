import os
from pathlib import Path
import re
import subprocess


_DOXYGEN_PATH="doxygen"


def _split_doxy_parts(line : str) -> "list[str]" :
	parts = []
	max = len(line)
	
	n = -1
	start_n = 0
	
	while True:
		n = n + 1
		if n >= max:
			if n - start_n > 0:
				parts.append(line[start_n:n])
			break

		c = line[n]
		if c == "\\":
			# Handle escape characters
			next_n = n + 1
			if next_n != max:
				n = n + 1
				if line[n] == "\\":
					continue
				elif line[n] == "\"":
					continue
				elif line[n] == "\n":
					if start_n > n - 1:
						parts.append(line[start_n:n])
					continue
				else:
					n = n - 1
					continue

		elif c == "\"":
			# Add to line if we have something teed up
			if start_n != n:
				parts.append(line[start_n:n])
				start_n = n

			# Skip quoted sections
			while True:
				n = n + 1
				if n >= max:
					break
				c = line[n]
				if c == "\"":
					n = n + 1
					break
		
			# Add to line if we have something teed up
			if start_n != n:
				parts.append(line[start_n:n])
				start_n = n

		elif c == "\n":
			if start_n != n:
				parts.append(line[start_n:n])
		elif c == " ":
			if n - start_n > 1:
				parts.append(line[start_n:n])
				start_n = n + 1

	o = []
	for v in parts:
		v = v.strip() or ""
		if v.startswith("\"") and v.endswith("\""):
			v = v.removeprefix("\"").removesuffix("\"")
		if len(v) != 0:
			o.append(v)
	return o
def _join_doxy_parts(parts : "list[str]", use_seperate_lines:bool = False, tabbing:str="\t") -> str:
	s = ""
	n = 0
	for v in parts:
		if n > 0:
			s += "\\\n" + tabbing
		if v.count(" ") != 0:
			s += f'"{v}"'
		else:
			s += v
		s += " "			
		n = n + 1
	return s


class DoxygenAttribute:

	def _proc_value(value : "str | list[str] | None") -> "list[str]" :
		if value is None:
			value = ""
		if type(value) != type(""):
			return value
		return _split_doxy_parts(value)

	def value_string(self) -> str:
		return _join_doxy_parts(self.values)

	def set_value(self, value : "str | list[str] | None"):
		self.values = DoxygenAttribute._proc_value(value)

	def __str__(self) -> str :
		return f"{self.name} = {self.value_string()}"

	def __init__(self, name : str, value : "str | list[str] | None" = None):
		self.name = name
		self.values = DoxygenAttribute._proc_value(value)


def _is_doxy_comment(s : str) -> bool :
	return s.count("#") != 0
def _is_empty_str(s : str) -> bool:
	return len(s.strip()) == 0
	
def _process_doxy_lines(s : "list[str]") -> "list[str]" :
	o = []
	for v in s:
		line = v.strip()
		if len(line) == 0:
			continue
		if not _is_doxy_comment(line):
			o.append(line)
	return o
def _process_doxy(s : str) -> str:
	lines = s.splitlines(False)
	lines = _process_doxy_lines(lines)
	return "\n".join(lines)

_DOXY_ATTRIB_NAME_REGEX = re.compile("[^=]*")
_DOXY_ATTRIB_VALUE_CLEAN_REGEX = re.compile("=(.*)")

def _parse_value_helper(value_strings : "list[str]") -> str:
	return " ".join(value_strings)

def _parse_doxy_attributes_from_lines(lines : "list[str]") -> "list[DoxygenAttribute]":

	attribs = []
	
	cur_attrib = None
	cur_values = None

	for line in lines:
		s = line
		
		# If no attribute is being parsed, determine the name of this one
		if cur_attrib is None:
			name = _DOXY_ATTRIB_NAME_REGEX.match(s)
			if name is not None:
				name = name.group(0)
				cur_attrib = DoxygenAttribute(name.strip())
				s = s.removeprefix(cur_attrib.name).strip()
				if s.startswith("="):
					s = s.removeprefix("=")
				s = s.strip()

		if cur_attrib is not None:
			if len(s) > 0:
				if cur_values is None:
					cur_values : "list[str]" = []
				s = s.strip()
				if s.endswith("\\"):
					cur_values.append(s.removesuffix("\\"))
				else:
					cur_values.append(s)
					cur_attrib.set_value(_parse_value_helper(cur_values))
					attribs.append(cur_attrib)
					cur_values = None
					cur_attrib = None
			else:
				if cur_values is not None:
					cur_values = _parse_value_helper(cur_values)
				cur_attrib.set_value(cur_values)
				attribs.append(cur_attrib)
				cur_attrib = None
				cur_values = None

	if cur_attrib is not None:
		attribs.append(cur_attrib)
		cur_attrib = None

	return attribs


class DoxygenConfig:

	def _find(self, name : str) -> "DoxygenAttribute | None":
		for v in self._attribs:
			if v.name == name:
				return v
		return None

	def get(self, name : str) -> "DoxygenAttribute | None ":
		return self._find(name)
	
	def get_value(self, name : str) -> "list[str]":
		attrib = self._find(name)
		if attrib:
			return attrib.values
		else:
			return []

	def set(self, name : str, values : "str | list[str] | None") :
		attrib = self._find(name)
		if not attrib:
			self._attribs.append(DoxygenAttribute(name, values))
		else:
			attrib.set_value(values)

	def save(self):
		f = open(self._path, "w")
		for v in self._attribs:
			f.write(f"{str(v)}\n\n")
		f.close()

	def load(self):
		f = open(self._path, "r", newline="\n")
		doxy_data = f.readlines()
		f.close()
		doxy_data = _process_doxy_lines(doxy_data)
		self._attribs = _parse_doxy_attributes_from_lines(doxy_data)

	def set_path(self, path : Path) :
		self._path = path

	def __init__(self, path : Path):
		self._path = path
		self._attribs = []
		if self._path.exists():
			self.load()
		

class Doxygen:

	def generate_proc(self, config : DoxygenConfig, stdout=None) -> subprocess.Popen :
		
		if not config._path.exists():
			config.save()

		proc_command = [
			str(_DOXYGEN_PATH),
			str(config._path.as_posix())
		]

		proc = subprocess.Popen(proc_command, stdout=stdout, text=True)
		return proc

	def generate(self, config : DoxygenConfig, stdout=None) -> bool :
		proc = self.generate_proc(config,stdout=stdout)		
		proc_result = proc.wait()
		return proc_result == 0

	def __init__(self):
		self._exec_path = "doxygen"
