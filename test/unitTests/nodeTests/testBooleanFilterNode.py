import unittest
import unittest.mock as mock
from stl.tree import ComparisonOperatorNode
from stl.signals import Signal, BooleanSignal
from .testBinaryOperation import BinaryOperationTest

class ComparisonOperatorNodeTest(BinaryOperationTest):
	def setUp(self):
		self.node: ComparisonOperatorNode = ComparisonOperatorNode()
		super().setUp()


# 			OPERATORS = {
#     '=': lambda x, y: x == y,
#     '!=': lambda x, y: x != y,
#     '>=': lambda x, y: x >= y,
#     '<=': lambda x, y: x <= y,
#     '>': lambda x, y: x > y,
#     '<': lambda x, y: x < y
# }