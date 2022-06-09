""" Implementation for ValueNode class used in STL ASTs """
from ..node import Node
from ....signals import BooleanSignal, Signal, SignalList


class ValueNode(Node):  # Abstract class
	""" Implementation of a Node representing a literal Value in STL formula."""

	def __init__(self):
		super().__init__()
		self.sign = 1
		self.value = None

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		return Signal.createConstant("ValueNodeSignal", self.value)

	# ValueNodes are generally part of e.g. time intervals for operators
	# Even in BooleanValidation contexts, they should return the actual value (not a booleanized version)
	def booleanValidate(self, signals: SignalList, plot: bool, booleanize=False) -> Signal:
		if booleanize:
			return BooleanSignal.createConstant("ValueNodeSignal", self.value)
		return Signal.createConstant("ValueNodeSignal", self.value)

	def text(self) -> str:
		return ('-' if self.sign < 0 else '') + str(self.value)
