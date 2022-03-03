import unittest
import unittest.mock as mock
from .helpers import getCosSignal, getShiftedCosSignal
from stl.signals.signalvalue import SignalValue
from .testBooleanFilterNode import ComparisonOperatorNodeTest
from stl.signals import Signal, BooleanSignal, SignalValue
import math

class BooleanFilterNodeGreaterThanOrEqualToTest(ComparisonOperatorNodeTest):
	def setUp(self):
		super().setUp()
		self.node.processToken('>=')

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
		s1 = Signal("1", [0,1,2], [10,11,12], [1,1,0])
		s2 = Signal("2", [0,1,2], [1,2,3], [1,1,0])
		rs = Signal('comparison', [0,1,2],[1,1,1],[0,0,0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		rs = Signal('comparison', [0,1,2], [0,0,0], [0,0,0])
		self.quantitativeValidationTestHelper(s2, s1, rs)
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal('comparison', [0,1,2],[1,1,1],[0,0,0])
		self.booleanValidationTestHelper(s1, s2, rs)
		self.booleanValidationTestHelper(s2, s1, rs)

	def testFalseySignals(self):
		s1 = Signal("1", [0,1,2], [-10,-11,-12], [-1,-1,0])
		s2 = Signal("2", [0,1,2], [-1,-2,-3], [-1,-1,0])
		rs = Signal('comparison', [0,1,2],[0,0,0],[0,0,0])
		self.quantitativeValidationTestHelper(s1, s2, rs)
		rs = Signal('comparison', [0,1,2], [1,1,1], [0,0,0])
		self.quantitativeValidationTestHelper(s2, s1, rs)
		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal('comparison', [0,1,2],[1,1,1],[0,0,0])
		self.booleanValidationTestHelper(s1, s2, rs)
		self.booleanValidationTestHelper(s2, s1, rs)

	def testVariableSignals(self):
		s1 = getCosSignal(10, booleanSignal = False)
		s2 = getShiftedCosSignal(10, booleanSignal = False)
		lastElement = SignalValue(9.5, 1, 0)
		rs = Signal("comparison", [x/10 for x in range(0, 95, 5)], [1, 1, 0, 1] * 5)
		rs.addCheckpoint(lastElement)
		rs.recomputeDerivatives()
		self.quantitativeValidationTestHelper(s1, s2, rs)


		rs = Signal('comparison', rs.getTimes(), [0, 1, 1, 1] * 5)
		rs.addCheckpoint(lastElement)
		rs.recomputeDerivatives()
		self.quantitativeValidationTestHelper(s2, s1, rs)


		s1 = BooleanSignal.fromSignal(s1)
		s2 = BooleanSignal.fromSignal(s2)
		rs = BooleanSignal('comparison', [x for x in range(10)], [i%2 for i in range(10)])
		rs.addCheckpoint(lastElement)
		self.booleanValidationTestHelper(s2, s1, rs)
		rs = BooleanSignal("comparison", [x for x in range(10)], [(i+1) % 2 for i in range(10)])
		rs.addCheckpoint(lastElement)
		self.booleanValidationTestHelper(s1, s2, rs)




if __name__ == "__main__":
	unittest.main()