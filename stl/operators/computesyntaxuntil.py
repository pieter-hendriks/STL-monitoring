""" Computatation of the Until operation using the syntax-based algorithm """
from ..signals import Signal
from typing import List
from ..utility import Interval
import numpy as np


def computeSyntaxUntil(childResults: List[Signal], interval: Interval) -> Signal:
	""" Uses the inefficient syntax-based algorithm to compute the timed Until operation. """
	output: Signal = Signal("timedUntil")
	# Finding the timestamps is non-trivial, we need unique points from both the start points of intervals and endpoints
	# And then compute the interval from that point on to have correct behaviour
	intervalEndTimes = [x - interval.getUpper() for x in childResults[0].getTimes() if x - interval.getUpper() >= 0]
	resultTimestamps = np.unique([round(x, 5) for x in intervalEndTimes])
	for t in resultTimestamps:
		rhsInterval = childResults[1].computeInterval(interval + t, half_open=False)
		values = []
		for j in range(rhsInterval.getCheckpointCount()):
			lhsInterval = childResults[0].computeInterval(Interval(t, rhsInterval.getTime(j)), half_open=False)
			values.append(min(rhsInterval.getValue(j), min(lhsInterval.getValues())))
		if values:
			output.emplaceCheckpoint(t, max(values))
	output.recomputeDerivatives()
	return output