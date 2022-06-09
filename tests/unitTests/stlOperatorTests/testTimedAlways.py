""" Test the timed always operation  """

import unittest
from stl.signals import Signal, BooleanSignal
from stl.utility import Interval

from stl.operators import computeTimedAlways


class TimedAlwaysTest(unittest.TestCase):
	""" Implementation of the test cases for TimedAlways """

	def setUp(self) -> None:
		super().setUp()

	def testQuantitativeEmptySignal(self):
		signal = Signal()
		expectedResult = Signal("timedAlways")
		interval = Interval(123, 125)  # Shouldn't matter
		# Test empty both
		self.assertEqual(computeTimedAlways(signal, interval), expectedResult)

	def testBooleanEmptySignal(self):
		signal = BooleanSignal()
		expectedResult = BooleanSignal("timedAlways")
		interval = Interval(0, 5)  # Shouldn't matter
		# Test empty both
		self.assertEqual(computeTimedAlways(signal, interval), expectedResult)

	def testSimpleSignal(self):
		signal = Signal('test', [0, 1], [0, 1], [1, 0])
		expectedResult = Signal('timedAlways', [0], [0], [0])
		interval = Interval(0, 1)
		self.assertEqual(computeTimedAlways(signal, interval), expectedResult)

	def testSmallSignal(self):
		signal = Signal('test', [0, 1, 2, 3, 4], [2, 7, 5, 4, -1], [5, -2, -1, -5, 0])
		interval = Interval(0, 4)
		expectedResult = Signal('timedAlways', [0], [-1], [0])
		self.assertEqual(computeTimedAlways(signal, interval), expectedResult)

		interval = Interval(0, 2)
		expectedResult = Signal('timedAlways', [0, 1, 2], [2, 4, -1], [2, -5, 0])
		self.assertEqual(computeTimedAlways(signal, interval), expectedResult)

		interval = Interval(2, 4)
		expectedResult = Signal('timedAlways', [0], [-1], [0])
		self.assertEqual(computeTimedAlways(signal, interval), expectedResult)

		interval = Interval(1, 2)
		expectedResult = Signal('timedAlways', [0, 1, 2], [5, 4, -1], [-1, -5, 0])
		self.assertEqual(computeTimedAlways(signal, interval), expectedResult)

		interval = Interval(1, 3)
		expectedResult = Signal('timedAlways', [0, 1], [4, -1], [-5, 0])
		self.assertEqual(computeTimedAlways(signal, interval), expectedResult)


if __name__ == "__main__":
	unittest.main()