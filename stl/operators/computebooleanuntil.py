""" Computation of the Until operation for the STL formalism using Boolean semantics """

from ..signals import SignalList, BooleanSignal, SignalValue
from ..utility import Interval, getTimeListIntersection


def computeBooleanUntil(size: int, childResults: SignalList, interval: Interval):
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