""" Module containing implementation for FloatValueNode for STL AST """

from .valuenode import ValueNode


class FloatValueNode(ValueNode):
	""" Node representing a floating point literal from an STL formula in STL AST """

	def __init__(self):
		super().__init__()
		self.integer = None
		self.fraction = None

	def processToken(self, token: str) -> None:
		if token == '-':
			self.sign *= -1
			return
		if token == '.':
			return

		if self.integer is None:
			self.integer = int(str(token))
			self.value = self.sign * self.integer
		else:
			self.fraction = token
			self.value = self.sign * float(str(self.integer) + '.' + str(self.fraction))
