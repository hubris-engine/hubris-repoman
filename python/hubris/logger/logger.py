
class Level:
	none    = 0

	error   = 1
	warn    = 2
	info    = 3
	debug   = 4

	all     = debug

# Logging level names
_LEVEL_NAMES = [
	"[?]",
	"[Error]",
	"[Warn]",
	"[Info]",
	"[Debug]"
]


class Logger:

	def log(self, level : Level, msg : str):
		if self.level >= level:
			print(f"{_LEVEL_NAMES[level]} {msg}")

	def log_warn(self, msg):
		self.log(Level.warn, msg)
	
	def log_error(self, msg):
		self.log(Level.error, msg)
	
	def log_info(self, msg):
		self.log(Level.info, msg)
	
	def log_debug(self, msg):
		self.log(Level.debug, msg)

	def __init__(self, level=Level.all):
		self.level = level
