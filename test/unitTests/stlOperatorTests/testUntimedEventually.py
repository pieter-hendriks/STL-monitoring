import unittest
from stl.signals import Signal
from stl.operators import computeUntimedEventually


class UntimedEventuallyTest(unittest.TestCase):
	""" Implementation of the tests for the timed eventually operation 
	
	Efficient algorithm only: syntax algorithm uses TRUE UNTIL signal, 
	which works as long as UNTIL works and this is tested separately.
	
	Quantitative semantics only for the same reason - Boolean semantics uses the 
	syntax algorithm, too."""

	def setUp(self):
		super().setUp()

	def testEmptySignal(self):
		empty = Signal()
		expectedResult = Signal("untimedEventually")
		self.assertEqual(computeUntimedEventually(empty), expectedResult)

	def testPositiveSignal(self):
		signal = Signal("in", [0, 1, 2, 3], [1, 5, 2, 3], [4, -3, 6, 0])
		expectedResult = Signal("untimedEventually", [0, 1, 1.66667, 2, 3], [5, 5, 3, 3, 3])
		expectedResult.recomputeDerivatives()
		self.assertEqual(computeUntimedEventually(signal), expectedResult)

	def testNegativeSignal(self):
		signal = Signal("in", [0, 1, 2, 3], [-1, -5, -2, -8], [-4, 3, -6, 0])
		expectedResult = Signal("untimedEventually", [0, 0.25, 1, 2, 3], [-1, -2, -2, -2, -8], [-4, 0, 0, -6, 0])
		self.assertEqual(computeUntimedEventually(signal), expectedResult)

	def testAlternatingSignal(self):
		signal = Signal("in", [0, 1, 2, 3], [1, -5, 2, -8], [-6, 7, -10, 0])
		expectedResult = Signal("untimedEventually", [0, 1, 2, 3], [2, 2, 2, -8], [0, 0, -10, 0])
		self.assertEqual(computeUntimedEventually(signal), expectedResult)

	def testSmallSignals(self):
		inputSignal: Signal = Signal('test', [0, 1, 2, 3, 4, 5], [-1, -1, 1, -1, -1, -1], [0, 2, -2, 0, 0, 0])
		expectedResult: Signal = Signal('untimedEventually', [0, 1, 2, 3, 4, 5], [1, 1, 1, -1, -1, -1], [0, 0, -2, 0, 0, 0])
		result = computeUntimedEventually(inputSignal)
		self.assertEqual(expectedResult, result)
		inputSignal: Signal = Signal('test', [3.0, 3.5, 4.0], [1, 1, -1], [0, -4, 0])
		expectedResult = Signal('untimedEventually', [3.0, 3.5, 4.0], [1, 1, -1], [0, -4, 0])
		result = computeUntimedEventually(inputSignal)
		self.assertEqual(expectedResult, result)