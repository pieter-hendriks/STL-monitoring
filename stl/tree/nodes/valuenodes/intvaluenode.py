""" Module containing implementation for IntegerValueNode for STL AST """

from .valuenode import ValueNode


class IntValueNode(ValueNode):
	""" Node representing an integer literal from an STL formula in STL AST """

	def processToken(self, token: str) -> None:
		if token == '-':
			self.sign *= -1
			return
		self.value = self.sign * int(str(token))
