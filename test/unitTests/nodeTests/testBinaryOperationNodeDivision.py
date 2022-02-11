from stl.tree import BinaryOperationNode
from .testBinaryOperation import BinaryOperationTest
from stl.signals import Signal, BooleanSignal, SignalList
import unittest
import unittest.mock as mock


class BinaryOperationNodeDivisionTest(BinaryOperationTest):
	def setUp(self):
		self.node: BinaryOperationNode = BinaryOperationNode()
		super().setUp()
		self.node.processToken("/")
		
	def testEmptyDivision(self):
		# Empty signal should return empty signal - name should be 'quotient', always
		s1: Signal = Signal('quotient')
		s2 = Signal("differentName")
		self.quantitativeValidationTestHelper(s1, s1, s1)
		self.quantitativeValidationTestHelper(s2, s2, s1)
		s1 = BooleanSignal('quotient')
		s2 = BooleanSignal("different")
		self.booleanValidationTestHelper(s1, s1, s1)
		self.booleanValidationTestHelper(s2, s2, s1)

	def testPosPosDivision(self):
		# Test quantitative semantics
		s1: Signal = Signal("s1", [0, 1, 2], [4, 5, 6], [1, 1, 0])
		s2: Signal = Signal("s2", [0, 1, 2], [2, 1, 4], [-1, 3, 0])
		rs = Signal('quotient', [0, 1, 2], [2, 5, 1.5], [3, -3.5, 0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		# Check reverse operand order correctness
		rs = Signal('quotient', [0, 1, 2], [0.5, 0.2, 2/3], [-0.3, 2/3-0.2, 0])
		self.quantitativeValidationTestHelper(s2, s1, rs)

		# Test boolean semantics
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal("quotient", [0, 1, 2], [1, 1, 1], [0, 0, 0])
		self.booleanValidationTestHelper(s1, s2, rs)
		# Check reverse operand order correctness
		# In boolean case, no change is expected here.
		# rs = BooleanSignal("quotient", [0, 1, 2], [1, 1, 1], [0, 0, 0])
		self.booleanValidationTestHelper(s2, s1, rs)
		
	def testPosNegDivision(self):
		# Test Quant semantics
		s1: Signal = Signal("s1", [0, 1, 2], [4, 6, 8], [2, 2, 0])
		s2: Signal = Signal("s2", [0, 1, 2], [-2, -3, -4], [-1, -1, 0])
		rs = Signal('quotient', [0, 1, 2], [-2, -2, -2], [0, 0, 0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		rs = Signal('quotient', [0, 1, 2], [-0.5, -0.5, -0.5], [0, 0, 0])
		self.quantitativeValidationTestHelper(s2, s1, rs)

		# test Boolean semantics 
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		with self.assertRaises(ZeroDivisionError):
			self.booleanValidationTestHelper(s1, s2, BooleanSignal())
		rs = BooleanSignal('quotient', [0, 1, 2], [0, 0, 0], [0, 0, 0])
		self.booleanValidationTestHelper(s2, s1, rs)

	def testNegNegDivision(self):
		s1: Signal = Signal("s1", [0, 1, 2], [-1, -2, -3], [-1, -1, 0])
		s2: Signal = Signal("s2", [0, 1, 2], [-2, -4, -6], [-2, -2, 0])
		rs = Signal('quotient', [0, 1, 2], [0.5, 0.5, 0.5], [0, 0, 0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		rs = Signal('quotient', [0, 1, 2], [2, 2, 2], [0, 0, 0])
		self.quantitativeValidationTestHelper(s2, s1, rs)
		# Test Boolean Variant - both Signals are negative values, so get converted to False (0)
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		with self.assertRaises(ZeroDivisionError):
			self.booleanValidationTestHelper(s1, s2, BooleanSignal())
		with self.assertRaises(ZeroDivisionError):
			self.booleanValidationTestHelper(s1, s2, BooleanSignal())

if __name__ == "__main__":
	unittest.main()