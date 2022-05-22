# Core utils


# Throw for failed test
class TestFailed(Exception):
	def __init__(self, test_name : str, failure_reason : str):
		s = f'Test "{str(test_name)}" failed'
		if failure_reason is not None:
			s += f' - "{str(failure_reason)}"'
		super().__init__(s)

class InvalidType(Exception): ...
		