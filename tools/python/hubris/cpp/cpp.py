from .type import Type
from .core import TestFailed
from .enum import Enum

import hubris

_TESTS = [
	Type,
	Enum
]

def _run_test(type) -> bool :
	try:
		type.__test__()
		return True
	except TestFailed as exc:
		hubris.log_error(f"{exc}")
		return False

def run_tests():
	for v in _TESTS:
		if not _run_test(v):
			hubris.log_error("Failed tests")
			return
	hubris.log_info("Passed tests")
	
