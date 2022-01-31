from .operationnode import BinaryOperationNode
from ....stlUtils import getPunctualIntersection
from numbers import Number
from ....stlUtils import getPunctualIntersection
from ....signals import SignalList, Signal, BooleanSignal
class SumNode(BinaryOperationNode):
	def __init__(self):
		super().__init__()

