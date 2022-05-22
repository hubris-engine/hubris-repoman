from .logger import Logger as Logger
from .logger import Level as LogLevel

_logger = None

def _get_logger():
	global _logger
	if _logger is None:
		_logger = Logger()
	return _logger

def log_warn(msg):
	_get_logger().log_warn(msg)

def log_error(msg):
	_get_logger().log_error(msg)

def log_info(msg):
	_get_logger().log_info(msg)
	
def log_debug(msg):
	_get_logger().log_debug(msg)

def set_log_level(level : LogLevel):
	_get_logger().level = level

