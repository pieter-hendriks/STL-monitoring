import unittest
from stl.signals import Signal
from stl.utility import Interval
from stl.operators import computeTimedEventually


class TimedEventuallyTest(unittest.TestCase):
	""" Implementation of the tests for the timed eventually operation 
	
	Efficient algorithm only: syntax algorithm uses TRUE UNTIL signal, 
	which works as long as UNTIL works and this is tested separately.
	
	Quantitative semantics only for the same reason - Boolean semantics uses the 
	syntax algorithm, too."""

	def setUp(self):
		super().setUp()

	def testEmptySignal(self):
		empty = Signal()
		interval = Interval(0, 5)  # shouldn't matter
		expectedResult = Signal("timedEventually")
		self.assertEqual(computeTimedEventually(empty, interval), expectedResult)

	def testUnitInterval(self):
		signal = Signal("in", [0, 1], [0, 1], [1, 0])
		interval = Interval(0, 0)
		expectedResult = Signal("timedEventually", [0, 1], [0, 1], [1, 0])
		self.assertEqual(computeTimedEventually(signal, interval), expectedResult)
		interval = Interval(0, 1)
		expectedResult = Signal("timedEventually", [0], [1], [0])
		self.assertEqual(computeTimedEventually(signal, interval), expectedResult)

	def testPositiveSignal(self):
		signal = Signal("in", [0, 1, 2, 3], [1, 5, 2, 8], [4, -3, 6, 0])
		interval = Interval(0, 1)
		expectedResult = Signal("timedEventually", [0, 1, 2], [5, 5, 8], [0, 3, 0])
		self.assertEqual(computeTimedEventually(signal, interval), expectedResult)
		interval = Interval(0, 2)
		expectedResult = Signal("timedEventually", [0, 1], [5, 8], [3, 0])
		self.assertEqual(computeTimedEventually(signal, interval), expectedResult)
		interval = Interval(2, 3)
		expectedResult = Signal("timedEventually", [0], [8], [0])
		self.assertEqual(computeTimedEventually(signal, interval), expectedResult)

	def testNegativeSignal(self):
		signal = Signal("in", [0, 1, 2, 3], [-1, -5, -2, -8], [-4, 3, -6, 0])
		interval = Interval(0, 1)
		expectedResult = Signal("timedEventually", [0, 1, 2], [-1, -2, -2], [-1, 0, 0])
		self.assertEqual(computeTimedEventually(signal, interval), expectedResult)
		interval = Interval(0, 2)
		expectedResult = Signal("timedEventually", [0, 1], [-1, -2], [-1, 0])
		self.assertEqual(computeTimedEventually(signal, interval), expectedResult)
		interval = Interval(2, 3)
		expectedResult = Signal("timedEventually", [0], [-2], [0])
		self.assertEqual(computeTimedEventually(signal, interval), expectedResult)

	def testSmallSignals(self):
		inputSignal: Signal = Signal("testSignal", [0, 1, 2, 3, 4, 5], [-1, -1, 1, 1, -1, -1], [0, 2, 0, -2, 0, 0])
		interval: Interval = Interval(0, 1)
		expectedResult: Signal = Signal("timedEventually", [0, 1, 2, 3, 4], [-1, 1, 1, 1, -1], [2, 0, 0, -2, 0])
		self.assertEqual(computeTimedEventually(inputSignal, interval), expectedResult)

		interval: Interval = Interval(0, 2)
		expectedResult: Signal = Signal("timedEventually", [0, 1, 2, 3], [1, 1, 1, 1], [0, 0, 0, 0])
		self.assertEqual(computeTimedEventually(inputSignal, interval), expectedResult)

		interval: Interval = Interval(0, 3)
		expectedResult: Signal = Signal("timedEventually", [0, 1, 2], [1, 1, 1], [0, 0, 0])
		self.assertEqual(computeTimedEventually(inputSignal, interval), expectedResult)

	def testSingularSignal(self):
		signal: Signal = Signal("test", [0], [1], [0])
		interval = Interval(0, 0)
		expectedResult = Signal("timedEventually", [0], [1], [0])
		self.assertEqual(computeTimedEventually(signal, interval), expectedResult)
		# Any non-singular interval will do here
		interval = Interval(0, 2)
		expectedResult = Signal("timedEventually")
		self.assertEqual(computeTimedEventually(signal, interval), expectedResult)
