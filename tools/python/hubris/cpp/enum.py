# Helper for enum<->string conversion table generation.

from msilib.schema import MsiPatchHeaders
import hubris
from .common import strip_block_comments, strip_line_comments
import re

_TEST_STRING = """
/**
 * @brief Result type returned by action callback functions.
*/
enum class ActionResult : i32
{
	ok = 0,
	error = 1,
	/**
	 * @brief Action was invalid.
	*/
	invalid_action_error,
	/**
	 * @brief Action does not have a thread associated with it.
	*/
	no_associated_thread_error,
	/**
	 * @brief Offset to start using for user defined action result codes. Any other value is reserved.
	*/
	user_result = 1000,
};
"""

_ENUM_CLASS_NAME_REGEX = re.compile("enum class ([a-zA-Z_]*)")
_ENUM_VALUE_NAME_REGEX = re.compile("^[a-zA-Z_]*")
_ENUM_VALUE_VALUE_REGEX = re.compile("=(.*)")

def make_pair_type(lhs, rhs):
	return f"std::pair<{lhs}, {rhs}>"
def make_array_type(t, len):
	return f"std::array<{t}, {len}>"


def make_enum_string_conversion_table_entry(enum_type_name : str, enum_value : str) -> str :
	pair_type = make_pair_type(enum_type_name, "const char*")
	return f'{pair_type}{{ {enum_type_name}::{enum_value}, "{enum_value}" }}'

def make_enum_string_conversion_table_from_values(enum_type_name : str, values : "list[EnumValue]"):
	enum_values = []
	for v in values:
		enum_values.append(make_enum_string_conversion_table_entry(enum_type_name, v.name))

	array_contents_str = ",\n".join(enum_values)
	array_type = make_array_type(make_pair_type(enum_type_name, "const char*"), len(enum_values))
	array_str = f"""{array_type}
{{
{array_contents_str}
}}
"""
	return array_str


class EnumValue:

	def __def__(self):
		o = self.name
		if len(self.value) != 0:
			o += f" = {self.value}"
		return o

	def __init__(self, name, value : "str | None" = None):
		self.name = name
		self.value = value or ""


class Enum:

	def make_conversion_array_def(self) -> str:
		return make_enum_string_conversion_table_from_values(self.name, self.values)


	def parse_from_string(enum_type_name, source_code) -> "Enum | None" :
		regex = re.compile(f"(enum class {enum_type_name})")
		m = regex.search(source_code)
		if m:
			enum_source_code = source_code[m.start(0):]
			return parse_enum(enum_source_code)
		else:
			return None





	def __def__(self) -> str:
		ov = []
		for v in self.values:
			ov.append(v.__def__())
		ovs = ",\n".join(ov)
		o = f"""enum class {self.name}
{{
{ovs}	
}};
"""
		return o
	
	def __init__(self, name : str, values : "list[EnumValue]" = []):
		self.name = name
		self.values = values

	def __test__():
		e = Enum.parse_from_string("ActionResult", _TEST_STRING)
		if e:
			es = e.make_conversion_array_def()
			hubris.log_info(es)
		else:
			hubris.log_info("not found")


def parse_enum(enum_str : str):
	s = enum_str
	s = strip_line_comments(strip_block_comments(s))
	lines : "list[str]" = []
	enum_type_name = ""

	inside_enum = False
	for v in s.splitlines():
		sv = v.strip()
		# Skip empty lines
		if len(sv) == 0:
			continue
		if True:
			m = _ENUM_CLASS_NAME_REGEX.search(sv)
			if m:
				ms = m.group(1)
				enum_type_name = str(ms)
		
		if inside_enum:
			if sv.startswith("};"):
				inside_enum = False
			else:
				sv = sv.removesuffix(",")
				lines.append(sv)
				continue
		if sv.startswith("{"):
			inside_enum = True
		elif sv.startswith("};"):
			inside_enum = False
			break

	values = []
	for v in lines:
		value_name = str(_ENUM_VALUE_NAME_REGEX.match(v).group(0))
		value_value = None
		if v.count("=") != 0:
			m = _ENUM_VALUE_VALUE_REGEX.search(v)
			if m:
				value_value = str(m.group(1)).strip()

		values.append(EnumValue(value_name, value_value))
	return Enum(enum_type_name, values)
