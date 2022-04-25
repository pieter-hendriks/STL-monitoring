import unittest
import unittest.mock as mock
from stl.tree import NegationNode
from stl.signals import Signal, BooleanSignal
from stl.tree.nodes.formulanodes.comparisonoperatornode import ComparisonOperatorNode
from .testUnaryOperation import UnaryOperationTest
from .helpers import getCosSignal


class NegationNodeTest(UnaryOperationTest):

	def setUp(self):
		self.node: NegationNode = NegationNode()
		super().setUp()

	def testEmptySignal(self):
		s1 = Signal("empty")
		rs = Signal("negation")
		self.quantitativeValidationTestHelper(s1, rs)
		s1 = BooleanSignal.fromSignal(s1)
		rs = BooleanSignal.fromSignal(rs)
		self.booleanValidationTestHelper(s1, rs)

	def testPositiveSignal(self):
		s1 = Signal("test", [0, 1, 2], [4, 5, 6], [1, 1, 0])
		rs = Signal('negation', [0, 1, 2], [-4, -5, -6], [-1, -1, 0])
		self.quantitativeValidationTestHelper(s1, rs)
		s1 = BooleanSignal.fromSignal(s1)
		rs = BooleanSignal.fromSignal(rs)
		self.booleanValidationTestHelper(s1, rs)

	def testNegativeSignal(self):
		s1 = Signal("test", [0, 1, 2], [-4, -5, -6], [-1, -1, 0])
		rs = Signal('negation', [0, 1, 2], [4, 5, 6], [1, 1, 0])
		self.quantitativeValidationTestHelper(s1, rs)
		s1 = BooleanSignal.fromSignal(s1)
		rs = BooleanSignal.fromSignal(rs)
		self.booleanValidationTestHelper(s1, rs)

	def testCosSignal(self):
		s1 = getCosSignal(4, booleanSignal=False)
		rs = Signal('negation', s1.getTimes(), [-x for x in s1.getValues()], [-d for d in s1.getDerivatives()])
		self.quantitativeValidationTestHelper(s1, rs)
		s1 = BooleanSignal.fromSignal(s1)
		rs = BooleanSignal(
		    'negation', s1.getTimes(), [1 if x == 0 else 0 for x in s1.getValues()], [0] * len(s1.getDerivatives())
		)
		self.booleanValidationTestHelper(s1, rs)


if __name__ == "__main__":
	unittest.main()