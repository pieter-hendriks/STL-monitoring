import unittest
import unittest.mock as mock
from stl.tree import BooleanFilterNode
from stl.signals import Signal, BooleanSignal
from .testBinaryOperation import BinaryOperationTest

class BooleanFilterNodeTest(BinaryOperationTest):
	def setUp(self):
		self.node: BooleanFilterNode = BooleanFilterNode()
		super().setUp()


# 			OPERATORS = {
#     '=': lambda x, y: x == y,
#     '!=': lambda x, y: x != y,
#     '>=': lambda x, y: x >= y,
#     '<=': lambda x, y: x <= y,
#     '>': lambda x, y: x > y,
#     '<': lambda x, y: x < y
# }