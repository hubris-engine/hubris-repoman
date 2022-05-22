
class Level:
	none    = 0

	error   = 1
	warn    = 2
	info    = 3
	debug   = 4

	all     = debug

class Logger:

	def log_warn(self, msg):
		if self.level >= Level.warn:
			print(f"[Warning] {msg}")
	
	def log_error(self, msg):
		if self.level >= Level.error:
			print(f"[Error] {msg}")
	
	def log_info(self, msg):
		if self.level >= Level.info:
			print(f"[Info] {msg}")
	
	def log_debug(self, msg):
		if self.level >= Level.debug:
			print(f"[Debug] {msg}")

	def __init__(self, level=Level.all):
		self.level = level
