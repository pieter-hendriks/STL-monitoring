""" Computation of the Until operation for the STL formalism using Boolean semantics """

from ..signals import BooleanSignal, SignalValue
from ..utility import Interval, getTimeListIntersection


def computeBooleanUntil(lhs: BooleanSignal, rhs: BooleanSignal, interval: Interval) -> BooleanSignal:
	""" Method implementing the boolean validation for the Until node. Syntax based algorithm. """
	lhs, rhs = BooleanSignal.computeComparableSignals(lhs, rhs)
	a = interval.getLower()
	b = interval.getUpper()
	# Get the true intervals of the signals
	lhsIntervals, rhsIntervals = [], []
	currentLhsInterval, currentRhsInterval = [], []
	previousLhsTrue, previousRhsTrue = False, False
	assert lhs.getCheckpointCount() == rhs.getCheckpointCount()
	size = lhs.getCheckpointCount()
	for i in range(size):
		if lhs.getValue(i) and not previousLhsTrue:
			previousLhsTrue = True
			currentLhsInterval.append(lhs.getTime(i))
		elif not lhs.getValue(i) and previousLhsTrue:
			previousLhsTrue = False
			# temp_1.append(result[0][0][i - 1])  # Closed interval (discrete time steps)
			currentLhsInterval.append(lhs.getTime(i))  # Half open interval [a,b) (continuous time steps)
			lhsIntervals.append(currentLhsInterval)
			currentLhsInterval = []

		if rhs.getValue(i) and not previousRhsTrue:
			previousRhsTrue = True
			currentRhsInterval.append(rhs.getTime(i))
		elif not rhs.getValue(i) and previousRhsTrue:
			previousRhsTrue = False
			# temp_2.append(result[1][0][i - 1])  # Closed interval (discrete time steps)
			currentRhsInterval.append(rhs.getTime(i))  # Half open interval [a,b) (continuous time steps)
			rhsIntervals.append(currentRhsInterval)
			currentRhsInterval = []
	if previousLhsTrue:
		currentLhsInterval.append(lhs.getTime(size - 1))
		lhsIntervals.append(currentLhsInterval)
	if previousRhsTrue:
		currentRhsInterval.append(rhs.getTime(size - 1))
		rhsIntervals.append(currentRhsInterval)

	# Decompose and calculate the Until for the decompositions
	resultIntervals = []
	for currentLhsInterval in lhsIntervals:
		for currentRhsInterval in rhsIntervals:
			intersection = getTimeListIntersection(currentLhsInterval, currentRhsInterval)
			if intersection:
				interval = [max(0, intersection[0] - b), min(size, intersection[1] - a)]
				assert interval[0] <= interval[1], "Non-existent interval, not sure how to handle this."
				intersection = getTimeListIntersection(interval, currentLhsInterval)
				if intersection:
					resultIntervals.append(intersection)
	# Calculate the entire until, make the intervals true in the until
	until = BooleanSignal("booleanTimedUntil", rhs.getTimes(), [0] * size)
	for untilInterval in resultIntervals:
		for timestamp in untilInterval:
			if timestamp in until.getTimes():
				timestampIndex = until.computeIndexForTime(timestamp)
				until.setValue(timestampIndex, 1)
			else:
				until.emplaceCheckpoint(timestamp, 1)
		intervalStartIndex = until.computeIndexForTime(untilInterval[0])
		intervalEndIndex = until.computeIndexForTime(untilInterval[1])
		for i in range(intervalStartIndex, intervalEndIndex):
			# Iteration (by index) over all time stamps in until part of the interval
			# Half-open interval, so exclude the last value.
			until.getCheckpoint(i).setValue(1)
		until.getCheckpoint(intervalEndIndex).setValue(0)
	for i in reversed(range(until.getCheckpointCount())):
		if until.getTime(i) > lhs.getTime(-1) - b:
			if until.getTime(i - 1) < lhs.getTime(-1) - b:
				poppedPoint: SignalValue = until.popCheckpoint()
				until.emplaceCheckpoint(lhs.getTime(-1) - b, poppedPoint.getValue())
			else:
				until.popCheckpoint()
	return until