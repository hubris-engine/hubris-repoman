from .core import InvalidType
from .type import Type


class Variable:

	def type(self) -> Type :
		return self._type
	
	def name(self) -> str :
		return self._name

	def __define__(self) -> str:
		return f'{str(self._type)} {self._name}'

	def __str__(self) -> str:
		return self._name

	def __init__(self, type : Type, name : str):
		self._name = name
		self._type = type
