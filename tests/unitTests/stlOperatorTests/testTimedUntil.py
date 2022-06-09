""" Test the timed until operation (both the efficient and syntax variants) """

import unittest
from stl.signals import Signal, BooleanSignal
from stl.utility import Interval

from stl.operators import computeTimedUntil, computeSyntaxUntil, computeBooleanUntil
from .untilTestData import TESTCASE1_INTERVAL_LOWERBOUND, TESTCASE1_INTERVAL_UPPERBOUND, TESTCASE1_LEFTCHILD_SIGNAL, TESTCASE1_RIGHTCHILD_SIGNAL
from .untilTestData import TESTCASE2_INTERVAL_LOWERBOUND, TESTCASE2_INTERVAL_UPPERBOUND, TESTCASE2_LEFTCHILD_SIGNAL, TESTCASE2_RIGHTCHILD_SIGNAL


class TimedUntilTest(unittest.TestCase):

	def setUp(self) -> None:
		super().setUp()

	def testEmptySignal(self):
		empty = Signal()
		nonEmpty = Signal("test", [0, 1, 2], [0, 1, 2], [1, 1, 0])
		expectedResult = Signal("timedUntil")
		interval = Interval(0, 5)  # Shouldn't matter
		# Test empty both
		self.assertEqual(computeTimedUntil(empty, empty, interval), expectedResult)
		self.assertEqual(computeSyntaxUntil(empty, empty, interval), expectedResult)
		# Test empty rhs
		self.assertEqual(computeTimedUntil(empty, nonEmpty, interval), expectedResult)
		self.assertEqual(computeSyntaxUntil(empty, nonEmpty, interval), expectedResult)
		# Test empty lhs
		self.assertEqual(computeTimedUntil(nonEmpty, empty, interval), expectedResult)
		self.assertEqual(computeSyntaxUntil(nonEmpty, empty, interval), expectedResult)

	def testBooleanEmptySignal(self):
		empty = BooleanSignal()
		nonEmpty = BooleanSignal("test", [0, 1, 2], [0, 1, 1])
		expectedResult = BooleanSignal("booleanTimedUntil")
		interval = Interval(0, 5)  # Shouldn't matter
		# Test empty both
		self.assertEqual(computeBooleanUntil(empty, empty, interval), expectedResult)
		# Test empty rhs
		self.assertEqual(computeBooleanUntil(empty, nonEmpty, interval), expectedResult)
		# Test empty lhs
		self.assertEqual(computeBooleanUntil(nonEmpty, empty, interval), expectedResult)

	def testSimpleSignalBoolean(self):
		signal = BooleanSignal('test', [0, 1], [0, 1], [1, 0])
		interval = Interval(0, 1)
		expectedResult = BooleanSignal('booleanTimedUntil', [0], [0], [0])
		self.assertEqual(computeBooleanUntil(signal, signal, interval), expectedResult)
		# This signal should be equal to the previous one - negative value should be converted to 0
		signal = BooleanSignal('test', [0, 1], [-1, 1], [2, 0])
		self.assertEqual(computeBooleanUntil(signal, signal, interval), expectedResult)
		# This signal should be equal to the previous one - big positive value should be converted to 1
		signal = BooleanSignal('test', [0, 1], [0, 5], [5, 0])
		self.assertEqual(computeBooleanUntil(signal, signal, interval), expectedResult)

	def testComplexSignalAlgorithmEquality(self):
		# Compare efficient to syntax algorithm - we don't have a predicted result for this case
		# That we expect to be entirely correct
		efficientResult = computeTimedUntil(
		    TESTCASE1_LEFTCHILD_SIGNAL, TESTCASE1_RIGHTCHILD_SIGNAL,
		    Interval(TESTCASE1_INTERVAL_LOWERBOUND, TESTCASE1_INTERVAL_UPPERBOUND)
		)
		syntaxResult = computeSyntaxUntil(
		    TESTCASE1_LEFTCHILD_SIGNAL, TESTCASE1_RIGHTCHILD_SIGNAL,
		    Interval(TESTCASE1_INTERVAL_LOWERBOUND, TESTCASE1_INTERVAL_UPPERBOUND)
		)
		self.assertEqual(efficientResult, syntaxResult)
		efficientResult = computeTimedUntil(
		    TESTCASE2_LEFTCHILD_SIGNAL, TESTCASE2_RIGHTCHILD_SIGNAL,
		    Interval(TESTCASE2_INTERVAL_LOWERBOUND, TESTCASE2_INTERVAL_UPPERBOUND)
		)
		syntaxResult = computeSyntaxUntil(
		    TESTCASE2_LEFTCHILD_SIGNAL, TESTCASE2_RIGHTCHILD_SIGNAL,
		    Interval(TESTCASE2_INTERVAL_LOWERBOUND, TESTCASE2_INTERVAL_UPPERBOUND)
		)
		self.assertEqual(efficientResult, syntaxResult)

	def testSimpleSignal(self):
		signal = Signal('test', [0, 1], [0, 1], [1, 0])
		expectedResult = Signal('timedUntil', [0], [0], [0])
		interval = Interval(0, 1)
		self.assertEqual(computeTimedUntil(signal, signal, interval), expectedResult)
		self.assertEqual(computeSyntaxUntil(signal, signal, interval), expectedResult)

	def testSmallSignal(self):
		left = Signal('test', [0, 1, 2, 3, 4], [2, 7, 5, 4, -1], [5, -2, -1, -5, 0])
		right = Signal('test', [0, 1, 2, 3, 4], [-1, -1, -1, 1, 1], [0, 0, 2, 0, 0])
		interval = Interval(0, 4)
		expectedResult = Signal('timedUntil', [0], [1], [0])
		self.assertEqual(computeTimedUntil(left, right, interval), expectedResult)
		self.assertEqual(computeSyntaxUntil(left, right, interval), expectedResult)

		interval = Interval(0, 2)
		expectedResult = Signal('timedUntil', [0, 1, 1.6, 2], [-1, 1, 1, 1], [2, 0, 0, 0])
		self.assertEqual(computeTimedUntil(left, right, interval), expectedResult)
		self.assertEqual(computeSyntaxUntil(left, right, interval), expectedResult)

		interval = Interval(2, 4)
		expectedResult = Signal('timedUntil', [0], [1], [0])
		self.assertEqual(computeTimedUntil(left, right, interval), expectedResult)
		self.assertEqual(computeSyntaxUntil(left, right, interval), expectedResult)

		interval = Interval(1, 2)
		expectedResult = Signal('timedUntil', [0, 1, 1.6, 2], [-1, 1, 1, 1], [2, 0, 0, 0])
		self.assertEqual(computeTimedUntil(left, right, interval), expectedResult)
		self.assertEqual(computeSyntaxUntil(left, right, interval), expectedResult)

		interval = Interval(1, 3)
		expectedResult = Signal('timedUntil', [0, 0.6, 1], [1, 1, 1], [0, 0, 0])
		self.assertEqual(computeTimedUntil(left, right, interval), expectedResult)
		self.assertEqual(computeSyntaxUntil(left, right, interval), expectedResult)

	def testBooleanUntilLhsTimes(self):
		lhs = BooleanSignal("l", [0, 1], [1, 0])
		rhs = BooleanSignal("r", [0, 1], [0, 1])
		interval = Interval(0, 1)
		expected = BooleanSignal("booleanTimedUntil", [0], [1])
		self.assertEqual(computeBooleanUntil(lhs, rhs, interval), expected)

	def testBooleanUntilRhsTimes(self):
		lhs = BooleanSignal("l", [0, 1], [0, 1])
		rhs = BooleanSignal("r", [0, 1], [1, 0])
		interval = Interval(0, 1)
		expected = BooleanSignal("booleanTimedUntil", [0], [0])
		self.assertEqual(computeBooleanUntil(lhs, rhs, interval), expected)

	def testBooleanUntilLargeTimegap(self):
		lhs = BooleanSignal("l", [0, 0.5, 2], [1, 1, 0])
		rhs = BooleanSignal("r", [0, 1.5, 2], [0, 0, 1])
		interval = Interval(0, 1)
		expected = BooleanSignal("booleanTimedUntil", [0, 0.5, 1], [0, 0, 1])
		self.assertEqual(computeBooleanUntil(lhs, rhs, interval), expected)

		lhs = BooleanSignal("l", [0, 0.5, 2], [1, 0, 0])
		rhs = BooleanSignal("r", [0, 1.5, 2], [0, 0, 1])
		interval = Interval(0, 1)
		expected = BooleanSignal("booleanTimedUntil", [0, 0.5, 1], [0, 0, 0])
		self.assertEqual(computeBooleanUntil(lhs, rhs, interval), expected)


if __name__ == "__main__":
	unittest.main()