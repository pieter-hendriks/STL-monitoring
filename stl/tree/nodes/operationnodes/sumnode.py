from .binaryoperationnode import BinaryOperationNode
from numbers import Number
from ....signals import SignalList, Signal, BooleanSignal
class SumNode(BinaryOperationNode):
	def __init__(self):
		super().__init__()

