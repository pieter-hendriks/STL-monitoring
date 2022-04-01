from .formulanode import FormulaNode
from ....stlUtils import getBooleanIntersection
from ....utility import Interval
from ....signals import Signal, BooleanSignal, SignalList, SignalValue
from typing import List
import warnings
from ....operators import computeTimedEventually, computeUntimedEventually, computeTimedUntil, computeUntimedUntil


class UntilNode(FormulaNode):

	def __init__(self) -> None:
		super().__init__()
		self.__useSyntaxAlgorithm = False

	def useSyntaxAlgorithm(self):
		self.__useSyntaxAlgorithm = True

	def useEfficientAlgorithm(self):
		self.__useSyntaxAlgorithm = False

	def syntaxAlgorithm(self, size: int, childResults: List[Signal], interval: Interval) -> Signal:
		""" Uses the inefficient syntax-based algorithm to compute the timed Until operation. """
		output: Signal = Signal("timedUntil")
		for i in range(size):
			t = childResults[1].getTime(i)
			rhsInterval = childResults[1].computeInterval(interval + t, half_open=False)
			values = []
			derivatives = []
			for j in range(rhsInterval.getCheckpointCount()):
				k = rhsInterval.getTime(j)
				lhsInterval = childResults[0].computeInterval(Interval(t, k), half_open=False)
				values.append(min(rhsInterval.getValue(j), min(lhsInterval.getValues())))
				derivatives.append(min(rhsInterval.getDerivative(j), min(lhsInterval.getDerivatives())))
			if values:
				output.emplaceCheckpoint(t, max(values), max(derivatives))
		for i in reversed(range(output.getCheckpointCount())):
			updatedLastTime = childResults[0].getTime(-1) - interval.getUpper()
			if output.getTime(i) > updatedLastTime:
				sv = output.popCheckpoint()
				if sv.getTime() < updatedLastTime:
					output.emplaceCheckpoint(
					    updatedLastTime, output.computeInterpolatedValue(updatedLastTime),
					    output.getDerivative(-2)
					)
		output.recomputeDerivatives()
		output.simplify()
		return output

	def quantitativeValidate(self, signals: SignalList, plot: bool = False) -> Signal:
		if not self.__useSyntaxAlgorithm:
			if len(self.children) == 1:
				# Untimed eventually -- no time interval children, 1 signal child
				result = computeUntimedEventually(self.children[0].quantitativeValidate(signals, plot))
			elif len(self.children) == 2:
				# Untimed Until -- no time interval children, 2 signal children ( two time interval and no signal isn't a possibility)
				result = computeUntimedUntil(
				    self.children[0].quantitativeValidate(signals, plot),
				    self.children[1].quantitativeValidate(signals, plot)
				)
			elif len(self.children) >= 3:
				interval: Interval = Interval(
				    self.children[-3].quantitativeValidate(signals, plot).getValue(0),
				    self.children[-2].quantitativeValidate(signals, plot).getValue(0)
				)
				if len(self.children) == 4:  # timed until, 2 time interval children, 2 signal children
					result = computeTimedUntil(
					    self.children[0].quantitativeValidate(signals, plot),
					    self.children[3].quantitativeValidate(signals, plot), interval
					)
				else:
					# Timed eventually - 2 time interval children, 1 signal child (time interval must always be exactly 0 or exactly 2, so this is only option)
					result = computeTimedEventually(
					    self.children[-1].quantitativeValidate(signals, plot), interval
					)
			result.recomputeDerivatives()
			result.simplify()
			return result

		# TODO:
		# Code here needs some cleaning. The efficient algorithm's implementation now neatly handles all operators without needing any of the below code.
		# The syntax algorithm, however, may need to interval to be present, so may not operate at all if we have e.g. 1 or 2 children.
		# For now, to avoid dealing with that issue, I've left the code below unchanged for the short algorithm.
		# In case any long algorithm call is hit, it will assert False.

		warnings.warn("Falling back to old behaviour for short algorithm. Please fix.")

		# Check if one or two formula nodes as children, if one -> add true signal
		if len(self.children) == 4:
			childResults: SignalList = SignalList(
			    [
			        self.children[0].quantitativeValidate(signals, plot),
			        self.children[3].quantitativeValidate(signals, plot)
			    ]
			)
			childResults = SignalList(Signal.computeComparableSignals(childResults[0], childResults[1]))
		elif len(self.children) == 3:
			# Eventually: EVENTUALLY[a, b] <SIGNAL>: a = children[0]/[-3], b = [1]/[-2], signal = [2]/[-1]
			# This is the 'eventually' operation == '<TRUE> Until[a,b] <signal>'
			childResult: Signal = self.children[2].quantitativeValidate(signals, plot)
			dummySignal: Signal = Signal(
			    "DummyTrueSignal", childResult.getTimes(), [1] * childResult.getCheckpointCount(),
			    [0] * childResult.getCheckpointCount()
			)
			childResults: SignalList = SignalList([dummySignal, childResult])

		size = childResults[0].getCheckpointCount()
		# Get the interval limit values for the interval [a, b]
		aSignal: Signal = self.children[-3].quantitativeValidate(signals, plot)
		bSignal: Signal = self.children[-2].quantitativeValidate(signals, plot)
		assert aSignal.getCheckpointCount() == bSignal.getCheckpointCount(
		) == 1, f"Ambiguous interval sizes. These should be from ValueNodes, which return a single-value Signal."
		interval = Interval(aSignal.getValue(0), bSignal.getValue(0))
		if self.__useSyntaxAlgorithm:
			until = self.syntaxAlgorithm(size, childResults, interval)
		else:
			# TODO: Remove this once the above has been corrected.
			assert False, "This should be unreachable since recent changes. See TODO/warning above."
			#until = self.longAlgorithm(size, childResults, interval)
		if plot:
			self.quantitativePlot(until)
		return until

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		# Operator can be unary or binary;
		# Children are 2 integers from the time interval, plus one or two formulas.
		if len(self.children) == 4:
			childResults: SignalList = SignalList(
			    [
			        self.children[0].booleanValidate(signals, plot),
			        self.children[3].booleanValidate(signals, plot)
			    ]
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
		) == 1, f"Ambiguous interval sizes. These should be from ValueNodes, which return a single-value Signal."
		interval = Interval(aSignal.getValue(0), bSignal.getValue(0))
		until = self.booleanValidationImplementation(size, childResults, interval)
		if plot:
			self.plot(until)
		return until

	def booleanValidationImplementation(
	    self, size: int, childResults: SignalList, interval: Interval
	):
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
				temp_1.append(
				    childResults[0].getTime(i)
				)  # Half open interval [a,b) (continuous time steps)
				intervals_1.append(temp_1)
				temp_1 = []

			if childResults[1].getValue(i) and not true_2:
				true_2 = True
				temp_2.append(childResults[1].getTime(i))
			elif not childResults[1].getValue(i) and true_2:
				true_2 = False
				# temp_2.append(result[1][0][i - 1])  # Closed interval (discrete time steps)
				temp_2.append(
				    childResults[1].getTime(i)
				)  # Half open interval [a,b) (continuous time steps)
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
				intersection = getBooleanIntersection(inter_1, inter_2)
				if intersection:
					interval = [max(0, intersection[0] - b), min(size, intersection[1] - a)]
					if interval[0] > interval[1]:  # Interval doesn't exist
						continue
					intersection = getBooleanIntersection(interval, inter_1)
					if intersection:
						intervals_until.append(intersection)
		# Calculate the entire until, make the intervals true in the until
		until = BooleanSignal("until", childResults[1].getTimes(), [0] * size)
		for interval in intervals_until:
			for timestamp in interval:
				if timestamp in until.getTimes():
					timestampIndex = until.getTimes().index(timestamp)
					until.getCheckpoint(timestampIndex).setValue(1)
				else:
					until.emplaceCheckpoint(timestamp, 1)
			intervalStartIndex = until.getTimes().index(interval[0])
			intervalEndIndex = until.getTimes().index(interval[1])
			for i in range(intervalStartIndex, intervalEndIndex):
				# Iteration (by index) over all time stamps in until part of the interval
				# Half-open interval, so exclude the last value.
				until.getCheckpoint(i).setValue(1)
			until.getCheckpoint(intervalEndIndex).setValue(0)
		for i in reversed(range(until.getCheckpointCount())):
			if until.getTime(i) > childResults[0].getTime(-1) - b:
				if until.getTime(i - 1) < childResults[0].getTime(-1) - b:
					# TODO: Figure out if this code is working properly. Changing the time like that seems fucky.
					# SignalValue is edited to allow it specifically because of this (as of 13/01 - may see other dependencies later)
					# No extra sorting happens in the SortedList after this change - which may cause problems.
					# The asserts wrapping this code ensure no unexpected consequences propagate
					assert until.getTimes() == sorted(
					    until.getTimes()
					), "Time was unsorted prior to time modification."
					poppedPoint: SignalValue = until.popCheckpoint()
					until.emplaceCheckpoint(
					    childResults[0].getTime(-1) - b, poppedPoint.getValue(), poppedPoint.getDerivative()
					)
					assert until.getTimes() == sorted(until.getTimes()), "Time modification created an issue."
				else:
					until.popCheckpoint()
		return until