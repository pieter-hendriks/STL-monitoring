import unittest
from .helpers import getCosSignal, getShiftedCosSignal
from stl.signals.signalvalue import SignalValue
from .testComparisonOperatorNode import ComparisonOperatorNodeTest
from stl.signals import Signal, BooleanSignal, SignalValue


class ComparisonOperatorNodeEqualToTest(ComparisonOperatorNodeTest):

	def setUp(self):
		super().setUp()
		self.node.processToken('=')

	def testEmptySignal(self):
		s1 = Signal('empty')
		s2 = Signal("notempty", [0], [1], [0])
		rs = Signal('comparison')
		self.quantitativeValidationTestHelper(s1, s1, rs)
		self.quantitativeValidationTestHelper(s1, s2, rs)
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal.fromSignal(rs)
		self.booleanValidationTestHelper(s1, s1, rs)
		self.booleanValidationTestHelper(s1, s2, rs)

	def testTruthySignals(self):
		s1 = Signal("1", [0, 1, 2], [10, 11, 12], [1, 1, 0])
		s2 = Signal("2", [0, 1, 2], [1, 2, 3], [1, 1, 0])
		rs = Signal('comparison', [0, 1, 2], [0, 0, 0], [0, 0, 0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		self.quantitativeValidationTestHelper(s2, s1, rs)
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal('comparison', [0, 1, 2], [1, 1, 1], [0, 0, 0])
		self.booleanValidationTestHelper(s1, s2, rs)
		self.booleanValidationTestHelper(s2, s1, rs)

	def testFalseySignals(self):
		s1 = Signal("1", [0, 1, 2], [-10, -11, -12], [-1, -1, 0])
		s2 = Signal("2", [0, 1, 2], [-1, -2, -3], [-1, -1, 0])
		rs = Signal('comparison', [0, 1, 2], [0, 0, 0], [0, 0, 0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		self.quantitativeValidationTestHelper(s2, s1, rs)
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal('comparison', [0, 1, 2], [1, 1, 1], [0, 0, 0])
		self.booleanValidationTestHelper(s1, s2, rs)
		self.booleanValidationTestHelper(s2, s1, rs)

	def testVariableSignals(self):
		s1 = getCosSignal(10, booleanSignal=False)
		s2 = getShiftedCosSignal(10, booleanSignal=False)
		# only last element is equal
		lastElement = SignalValue(9.5, 1, 0)
		rs = Signal("comparison", [x for x in range(10)], [1] * 10, [0] * 10)
		rs.addCheckpoint(lastElement)
		self.quantitativeValidationTestHelper(s1, s1, rs)

		rs = Signal("comparison", [x / 10 for x in range(0, 95, 5)], ([0, 1, 0, 1] * 5)[:-1])
		rs.addCheckpoint(lastElement)
		rs.recomputeDerivatives()
		self.quantitativeValidationTestHelper(s1, s2, rs)
		self.quantitativeValidationTestHelper(s2, s1, rs)

		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal('comparison', [x for x in range(10)], [0] * 10)
		rs.addCheckpoint(lastElement)
		self.booleanValidationTestHelper(s1, s2, rs)
		self.booleanValidationTestHelper(s2, s1, rs)

	def testVariableSignalsWithMultipleEqualities(self):
		s1 = Signal('s1', [0, 1, 2, 3, 4, 5, 6, 7, 8], [1, 0, 2, 3, 0, 4, 5, 6, 0], [-1, 2, 1, -3, 4, 1, 1, -6, 0])
		s2 = Signal(
		    's2', [0, 1, 2, 3, 4, 5, 6, 7, 8], [1, -4, 5, 3, -5, -95, 5, 2, 0], [-5, 9, -2, -8, -90, 100, -3, -2, 0]
		)
		rs = Signal('comparison', [0, 1, 11 / 7, 2, 3, 4, 5, 6, 7, 8], [1, 0, 1, 0, 1, 0, 0, 1, 0, 1])  # autocompute derivs
		self.quantitativeValidationTestHelper(s1, s2, rs)
		self.quantitativeValidationTestHelper(s2, s1, rs)

		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal(
		    'comparison', [0, 1, 2, 3, 4, 5, 6, 7, 8], [1, 1, 1, 1, 1, 0, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0]
		)
		self.booleanValidationTestHelper(s1, s2, rs)
		self.booleanValidationTestHelper(s2, s1, rs)


if __name__ == "__main__":
	unittest.main()