# pylint: disable=missing-module-docstring
from typing import List
# pylint: enable=missing-module-docstring
import numpy as np
from .formulanode import FormulaNode
from ....stlUtils import getTimeListIntersection
from ....utility import Interval
from ....signals import Signal, BooleanSignal, SignalList, SignalValue
from ....operators import computeTimedEventually, computeUntimedEventually, computeTimedUntil, computeUntimedUntil


class UntilNode(FormulaNode):
	""" Node representing the Until operation in STL formulas """

	def __init__(self) -> None:
		super().__init__()
		self.__useSyntaxAlgorithm = False

	def useSyntaxAlgorithm(self):
		""" Sets the Until node to use the Syntax (inefficient) algorithm implementation. """
		self.__useSyntaxAlgorithm = True

	def useEfficientAlgorithm(self):
		""" Sets the Until node to use the efficient algorithm implementation. """
		self.__useSyntaxAlgorithm = False

	# pylint: disable=no-self-use
	def syntaxAlgorithm(self, childResults: List[Signal], interval: Interval) -> Signal:
		""" Uses the inefficient syntax-based algorithm to compute the timed Until operation. """
		output: Signal = Signal("timedUntil")
		# Finding the timestamps is non-trivial, we need unique points from both the start points of intervals and endpoints
		# And then compute the interval from that point on to have correct behaviour
		intervalStartTimes = [
		    x for x in childResults[0].getTimes() if childResults[0].getLargestTime() - interval.getUpper() >= x
		]
		intervalEndTimes = [x - interval.getUpper() for x in childResults[0].getTimes() if x - interval.getUpper() >= 0]
		resultTimestamps = sorted(np.unique([round(x, 5) for x in [*intervalStartTimes, *intervalEndTimes]]))

		for t in resultTimestamps:
			rhsInterval = childResults[1].computeInterval(interval + t, half_open=False)
			values = []
			for j in range(rhsInterval.getCheckpointCount()):
				lhsInterval = childResults[0].computeInterval(Interval(t, rhsInterval.getTime(j)), half_open=False)
				values.append(min(rhsInterval.getValue(j), min(lhsInterval.getValues())))
			if values:
				output.emplaceCheckpoint(t, max(values))

		for i in reversed(range(output.getCheckpointCount())):
			updatedLastTime = childResults[0].getTime(-1) - interval.getUpper()
			if output.getTime(i) > updatedLastTime:
				sv = output.popCheckpoint()
				if sv.getTime() < updatedLastTime:
					output.emplaceCheckpoint(updatedLastTime, output.computeInterpolatedValue(updatedLastTime))
		output.recomputeDerivatives()
		return output

	# pylint: enable=no-self-use

	def __handleEfficientAlgorithm(self, signals: SignalList, plot: bool) -> Signal:
		if len(self.children) in [2, 4]:
			childSignals = SignalList(
			    Signal.computeComparableSignals(
			        self.children[0].quantitativeValidate(signals, plot),
			        self.children[-1].quantitativeValidate(signals, plot)
			    )
			)
		if len(self.children) == 1:
			# Untimed eventually -- no time interval children, 1 signal child
			result = computeUntimedEventually(self.children[0].quantitativeValidate(signals, plot))
		elif len(self.children) == 2:
			# Untimed Until -- no time interval children, 2 signal children (can't have time, no signal)
			result = computeUntimedUntil(childSignals[0], childSignals[1])
		elif len(self.children) >= 3:
			interval: Interval = Interval(
			    self.children[-3].quantitativeValidate(signals, plot).getValue(0),
			    self.children[-2].quantitativeValidate(signals, plot).getValue(0)
			)
			if len(self.children) == 4:  # timed until, 2 time interval children, 2 signal children
				result = computeTimedUntil(childSignals[0], childSignals[1], interval)
			else:
				# Timed eventually - 2 time interval children, 1 signal child (time can't have 1 child, so only option)
				result = computeTimedEventually(self.children[-1].quantitativeValidate(signals, plot), interval)
		return result

	def __handleSyntaxAlgorithm(self, signals: SignalList, plot: bool) -> Signal:
		# If we have four children, we have a timed until operation (lhs, interval (lower & upper), rhs)
		if len(self.children) == 4:
			childResults: SignalList = SignalList(
			    Signal.computeComparableSignals(
			        self.children[0].quantitativeValidate(signals, plot),
			        self.children[3].quantitativeValidate(signals, plot)
			    )
			)
			name = "timedUntil"
		# If we have three children, we have a timed eventually operation (interval (lower & upper), rhs)
		elif len(self.children) == 3:
			childResults: SignalList = SignalList(
			    Signal.computeComparableSignals(
			        Signal.createConstant('DummyTrueSignal', 1), self.children[2].quantitativeValidate(signals, plot)
			    )
			)
			name = "timedEventually"
		# If we have two children, we have an untimed until operation (lhs, rhs)
		elif len(self.children) == 2:
			childResults: SignalList = SignalList(
			    Signal.computeComparableSignals(
			        self.children[0].quantitativeValidate(signals, plot),
			        self.children[1].quantitativeValidate(signals, plot)
			    )
			)
			name = "untimedUntil"
		# Else we must have 1 child, which is the untimed eventually operation (rhs)
		else:
			assert len(self.children) == 1, "Invalid amount of children for until node."
			childResults: SignalList = SignalList(
			    Signal.computeComparableSignals(
			        Signal.createConstant('DummyTrueSignal', 1), self.children[0].quantitativeValidate(signals, plot)
			    )
			)
			name = "untimedEventually"
		# Get the interval limit values for the interval [a, b]
		# Untimed operation
		aSignal: Signal = Signal.createConstant('a', 0)
		bSignal: Signal = Signal.createConstant('b', float('inf'))
		if len(self.children) >= 3:
			# Timed operation
			aSignal: Signal = self.children[-3].quantitativeValidate(signals, plot)
			bSignal: Signal = self.children[-2].quantitativeValidate(signals, plot)

		assert all(x == s.getValue(0) for s in [aSignal, bSignal] for x in s.getValues())
		interval = Interval(aSignal.getValue(0), bSignal.getValue(0))
		result = self.syntaxAlgorithm(childResults, interval)
		result.setName(name)
		return result

	def quantitativeValidate(self, signals: SignalList, plot: bool = False) -> Signal:
		if not self.__useSyntaxAlgorithm:
			result: Signal = self.__handleEfficientAlgorithm(signals, plot)
		else:
			result: Signal = self.__handleSyntaxAlgorithm(signals, plot)
		result.recomputeDerivatives()
		self.quantitativePlot(plot, result)
		return result

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		# Operator can be unary or binary;
		# Children are 2 integers from the time interval, plus one or two formulas.
		if len(self.children) == 4:
			childResults: SignalList = SignalList(
			    [self.children[0].booleanValidate(signals, plot), self.children[3].booleanValidate(signals, plot)]
			)
			childResults = SignalList(Signal.computeComparableSignals(childResults[0], childResults[1]))
		else:
			assert len(self.children) == 3
			childResult: BooleanSignal = self.children[2].booleanValidate(signals, plot)
			dummySignal: BooleanSignal = BooleanSignal(
			    "DummyTrueSignal", childResult.getTimes(), [1] * childResult.getCheckpointCount(),
			    [0] * childResult.getCheckpointCount()
			)
			childResults: SignalList = SignalList([dummySignal, childResult])
		size = childResults[0].getCheckpointCount()

		aSignal: BooleanSignal = self.children[-3].booleanValidate(signals, plot)
		bSignal: BooleanSignal = self.children[-2].booleanValidate(signals, plot)
		assert aSignal.getCheckpointCount() == bSignal.getCheckpointCount(
		) == 1, "Ambiguous interval sizes. These should be from ValueNodes, which return a single-value Signal."
		interval = Interval(aSignal.getValue(0), bSignal.getValue(0))
		until = self.booleanValidationImplementation(size, childResults, interval)
		self.booleanPlot(plot, until)
		return until

	# pylint: disable=no-self-use,too-many-locals,too-many-branches,too-many-statements
	def booleanValidationImplementation(self, size: int, childResults: SignalList, interval: Interval):
		""" Method implementing the boolean validation for the Until node. Syntax based algorithm. """
		a = interval.getLower()
		b = interval.getUpper()
		# Get the true intervals of the signals
		intervals_1, intervals_2 = [], []
		temp_1, temp_2 = [], []
		true_1, true_2 = False, False

		for i in range(size):
			if childResults[0].getValue(i) and not true_1:
				true_1 = True
				temp_1.append(childResults[0].getTime(i))
			elif not childResults[0].getValue(i) and true_1:
				true_1 = False
				# temp_1.append(result[0][0][i - 1])  # Closed interval (discrete time steps)
				temp_1.append(childResults[0].getTime(i))  # Half open interval [a,b) (continuous time steps)
				intervals_1.append(temp_1)
				temp_1 = []

			if childResults[1].getValue(i) and not true_2:
				true_2 = True
				temp_2.append(childResults[1].getTime(i))
			elif not childResults[1].getValue(i) and true_2:
				true_2 = False
				# temp_2.append(result[1][0][i - 1])  # Closed interval (discrete time steps)
				temp_2.append(childResults[1].getTime(i))  # Half open interval [a,b) (continuous time steps)
				intervals_2.append(temp_2)
				temp_2 = []
		if true_1:
			temp_1.append(childResults[0].getTime(size - 1))
			intervals_1.append(temp_1)
		if true_2:
			temp_2.append(childResults[1].getTime(size - 1))
			intervals_2.append(temp_2)

		# Decompose and calculate the Until for the decompositions
		intervals_until = []
		for inter_1 in intervals_1:
			for inter_2 in intervals_2:
				intersection = getTimeListIntersection(inter_1, inter_2)
				if intersection:
					interval = [max(0, intersection[0] - b), min(size, intersection[1] - a)]
					if interval[0] > interval[1]:  # Interval doesn't exist
						continue
					intersection = getTimeListIntersection(interval, inter_1)
					if intersection:
						intervals_until.append(intersection)
		# Calculate the entire until, make the intervals true in the until
		until = BooleanSignal("until", childResults[1].getTimes(), [0] * size)
		for untilInterval in intervals_until:
			for timestamp in untilInterval:
				if timestamp in until.getTimes():
					timestampIndex = until.getTimes().index(timestamp)
					until.getCheckpoint(timestampIndex).setValue(1)
				else:
					until.emplaceCheckpoint(timestamp, 1)
			intervalStartIndex = until.getTimes().index(untilInterval[0])
			intervalEndIndex = until.getTimes().index(untilInterval[1])
			for i in range(intervalStartIndex, intervalEndIndex):
				# Iteration (by index) over all time stamps in until part of the interval
				# Half-open interval, so exclude the last value.
				until.getCheckpoint(i).setValue(1)
			until.getCheckpoint(intervalEndIndex).setValue(0)
		for i in reversed(range(until.getCheckpointCount())):
			if until.getTime(i) > childResults[0].getTime(-1) - b:
				if until.getTime(i - 1) < childResults[0].getTime(-1) - b:
					assert until.getTimes() == sorted(until.getTimes()), "Time was unsorted prior to time modification."
					poppedPoint: SignalValue = until.popCheckpoint()
					until.emplaceCheckpoint(childResults[0].getTime(-1) - b, poppedPoint.getValue(), poppedPoint.getDerivative())
					assert until.getTimes() == sorted(until.getTimes()), "Time modification created an issue."
				else:
					until.popCheckpoint()
		return until
		# pylint: enable=no-self-use,too-many-locals,too-many-branches,too-many-statements
