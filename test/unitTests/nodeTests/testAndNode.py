import unittest
import unittest.mock as mock
from stl.tree import AndNode
from stl.signals import Signal, BooleanSignal, booleansignal
from .testBinaryOperation import BinaryOperationTest
from .helpers import getCosSignal, getShiftedCosSignal
import math

class AndNodeTest(BinaryOperationTest):
	def setUp(self):
		self.node: AndNode = AndNode()
		super().setUp()

	def testEmptySignalAnd(self):
		s1 = Signal("empty")
		s2 = Signal("nonempty", [0], [0], [0])
		rs = Signal("and")
		self.quantitativeValidationTestHelper(s1, s1, rs)
		self.quantitativeValidationTestHelper(s1, s2, rs)
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal.fromSignal(rs)
		self.booleanValidationTestHelper(s1, s1, rs)
		self.booleanValidationTestHelper(s1, s2, rs)

	def testFalseySignals(self):
		s1 = Signal("falsey", [0, 1, 2], [-1, -2, -3], [-1, -1, 0])
		s2 = Signal("falsey2", [0, 1, 2], [-3, -2, -1], [1, 1, 0])
		rs = Signal("and", [0,1,2], [-3, -2, -3], [1, -1, 0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		self.quantitativeValidationTestHelper(s2, s1, rs)
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal.fromSignal(rs)
		self.booleanValidationTestHelper(s1, s2, rs)
		self.booleanValidationTestHelper(s2, s1, rs)

	def testTruthySignals(self):
		s1 = Signal("Truthy", [0, 1, 2], [1, 2, 3], [1, 1, 0])
		s2 = Signal("Truthy2", [0, 1, 2], [3, 2, 1], [-1, -1, 0])
		rs = Signal("and", [0,1,2], [1, 2, 1], [1, -1, 0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		self.quantitativeValidationTestHelper(s2, s1, rs)
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal.fromSignal(rs)
		self.booleanValidationTestHelper(s1, s2, rs)
		self.booleanValidationTestHelper(s2, s1, rs)

	def testCosSignals(self):
		s1 = Signal('cos', [0, 1, 2, 3], [1, -1, 1, -1], [-2, 2, -2, 0])
		s2 = Signal('cos2', [0, 1, 2, 3], [-1, 1, -1, 1], [2, -2, 2, 0])
		rs = Signal('and', [0, 0.5, 1, 1.5, 2, 2.5, 3], [-1, 0, -1, 0, -1, 0, -1], [2, -2, 2, -2, 2, -2, 0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		self.quantitativeValidationTestHelper(s2, s1, rs)

		s1 = getCosSignal(10, booleanSignal=False)
		s2 = getShiftedCosSignal(10, booleanSignal=False)
		intersectedTimes = [int(i/10) if int(i/10) == i/10 else i/10 for i in range(0, 91, 5)] + [9.5]
		intersectedValues = [[-1.0, 0.0][i%2] for i in range(len(intersectedTimes)-1)] + [0]
		intersectedDerivatives = [math.pow(-1, i) * 2.0 for i in range(len(intersectedTimes)-1)] + [0]
		rs = Signal("and", intersectedTimes, intersectedValues, intersectedDerivatives)
		self.quantitativeValidationTestHelper(s1, s2, rs)
		self.quantitativeValidationTestHelper(s2, s1, rs)


if __name__ == "__main__":
	unittest.main()