# Common tooling

import re

_COMMENT_BLOCK_REGEX = re.compile("/\*.*?\*/", re.DOTALL)
_COMMENT_LINE_REGEX = re.compile("//.*")

_STRING_LITERAL_REGEX = re.compile('"[^"]*"')

def strip_block_comments(s : str) -> str:
	return _COMMENT_BLOCK_REGEX.sub("", s)
	
def strip_string_literal_from_line(s : str) -> str:
	return _STRING_LITERAL_REGEX.sub("", s)

def strip_line_comments(s : str) -> str:
	return _COMMENT_LINE_REGEX.sub("", s)
	