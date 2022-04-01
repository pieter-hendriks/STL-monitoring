from ..node import Node
from typing import Union
from ....signals import Signal, BooleanSignal, SignalList
import math


class ValueNode(Node):  # Abstract class

	def __init__(self):
		super().__init__()
		self.sign = 1
		self.value = None

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		return Signal.createConstant("ValueNodeSignal", self.value, [0, float('inf')])

	# ValueNodes are generally part of e.g. time intervals for operators
	# Even in BooleanValidation contexts, they should return the actual value (not a booleanized version)
	def booleanValidate(self, signals: SignalList, plot: bool) -> Signal:
		return Signal.createConstant("ValueNodeSignal", self.value, [0, float('inf')])

	def text(self) -> str:
		return ('-' if self.sign < 0 else '') + str(self.value)