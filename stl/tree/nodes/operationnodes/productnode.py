from .operationnode import BinaryOperationNode
from stl.stlUtils import getPunctualIntersection
from numbers import Number
from ....signals import Signal, BooleanSignal, SignalList

class ProductNode(BinaryOperationNode):
	def __init__(self):
		super().__init__()
