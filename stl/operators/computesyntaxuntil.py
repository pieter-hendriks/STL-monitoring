""" Computatation of the Until operation using the syntax-based algorithm """
from ..signals import Signal
from typing import List
from ..utility import Interval
import numpy as np


def computeSyntaxUntil(lhsSignal: Signal, rhsSignal: Signal, interval: Interval) -> Signal:
	""" Uses the inefficient syntax-based algorithm to compute the timed Until operation. """
	lhsSignal, rhsSignal = Signal.computeComparableSignals(lhsSignal, rhsSignal)
	output: Signal = Signal("timedUntil")
	# Finding the timestamps is non-trivial, we need unique points from both the start points of intervals and endpoints
	# And then compute the interval from that point on to have correct behaviour
	resultTimestamps = [round(x - interval.getUpper(), 5) for x in lhsSignal.getTimes() if x - interval.getUpper() >= 0]
	for t in resultTimestamps:
		rhsInterval = rhsSignal.computeInterval(interval + t, half_open=False)
		values = []
		for j in range(rhsInterval.getCheckpointCount()):
			lhsInterval = lhsSignal.computeInterval(Interval(t, rhsInterval.getTime(j)), half_open=False)
			values.append(min(rhsInterval.getValue(j), min(lhsInterval.getValues())))
		if values:
			output.emplaceCheckpoint(t, max(values))
	output.recomputeDerivatives()
	return output