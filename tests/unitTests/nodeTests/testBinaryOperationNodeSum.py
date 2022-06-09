import unittest
import unittest.mock as mock
from .testBinaryOperation import BinaryOperationTest
from stl.tree import BinaryOperationNode
from stl.signals import Signal, BooleanSignal

class BinaryOperationNodeSumTest(BinaryOperationTest):
	def setUp(self):
		self.node: BinaryOperationNode = BinaryOperationNode()
		super().setUp()
		self.node.processToken("+")
		
	def testEmptySum(self):
		s1: Signal = Signal()
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s1
		# Empty signal sum should return empty signal
		self.assertEqual(Signal('sum'), self.node.quantitativeValidate(None, None))
		s1 = BooleanSignal()
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s1
		# Empty signal sum should return empty signal
		self.assertEqual(BooleanSignal('sum'), self.node.booleanValidate(None, None))

	def testPosPosSum(self):
		s1: Signal = Signal("s1", [0, 1, 2], [4, 5, 6], [1, 1, 0])
		s2: Signal = Signal("s2", [0, 1, 2], [2, 1, 4], [-1, 3, 0])
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		rs = Signal('sum', [0, 1, 2], [6, 6, 10], [0, 4, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# Sum is unchanged over operand order
		self.leftChild.quantitativeValidate.return_value = s2
		self.rightChild.quantitativeValidate.return_value = s1
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))

		# BooleanSignal test: should just be Truthy values.
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		rs = BooleanSignal("sum", [0, 1, 2], [1, 1, 1], [0, 0, 0])
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		# Since all values in pos-pos are truthy (that is, 1), operand swap doesn't change anything.
		self.leftChild.booleanValidate.return_value = s2
		self.rightChild.booleanValidate.return_value = s1
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		
	def testPosNegSum(self):
		s1: Signal = Signal("s1", [0, 1, 2], [4, 6, 8], [2, 2, 0])
		s2: Signal = Signal("s2", [0, 1, 2], [-2, -3, -4], [-1, -1, 0])
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		rs = Signal('sum', [0, 1, 2], [2, 3, 4], [1, 1, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# Operand order change doesn't changes the results
		self.leftChild.quantitativeValidate.return_value = s2
		self.rightChild.quantitativeValidate.return_value = s1
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))

		# test Boolean variant as well
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		rs = BooleanSignal('sum', [0,1,2], [1,1,1], [0,0,0])
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		# Swap the operands, result should be the same
		self.leftChild.booleanValidate.return_value = s2
		self.rightChild.booleanValidate.return_value = s1
		self.assertEqual(rs, self.node.booleanValidate(None, None))

	def testNegNegSum(self):
		s1: Signal = Signal("s1", [0, 1, 2], [-1, -2, -3], [-1, -1, 0])
		s2: Signal = Signal("s2", [0, 1, 2], [-2, -4, -6], [-2, -2, 0])
		self.leftChild.quantitativeValidate.return_value = s1
		self.rightChild.quantitativeValidate.return_value = s2
		rs = Signal('sum', [0, 1, 2], [-3, -6, -9], [-3, -3, 0])
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))
		# Sum operand order doesn't impact results
		self.leftChild.quantitativeValidate.return_value = s2
		self.rightChild.quantitativeValidate.return_value = s1
		self.assertEqual(rs, self.node.quantitativeValidate(None, None))

		# Test Boolean Variant - both Signals are negative values, so get converted to False (0)
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		# Then we expect all false sums
		rs = BooleanSignal('sum', [0,1,2], [0,0,0], [0,0,0])
		self.leftChild.booleanValidate.return_value = s1
		self.rightChild.booleanValidate.return_value = s2
		self.assertEqual(rs, self.node.booleanValidate(None, None))
		# And operand order doesn't impact that at all.
		self.leftChild.booleanValidate.return_value = s2
		self.rightChild.booleanValidate.return_value = s1
		self.assertEqual(rs, self.node.booleanValidate(None, None))

if __name__ == "__main__":
	unittest.main()