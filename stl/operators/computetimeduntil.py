""" STL Timed Until operation """
from ..utility import Interval
from ..signals import Signal
from .computeandor import computeAnd
from .computetimedeventually import computeTimedEventually
from .computetimedalways import computeTimedAlways
from .computeuntimeduntil import computeUntimedUntil


def computeTimedUntil(lhsSignal: Signal, rhsSignal: Signal, interval: Interval) -> Signal:
	""" Computes the timed until STL operation. Creates a new Signal instance to hold the result. 
	This method should be called with two signals that have equal sets of timestamps (i.e. after Signal.computeComparableSignals(lhs, rhs))"""
	assert lhsSignal.getTimes() == rhsSignal.getTimes(), "Expected equal timestamps."

	assert isinstance(lhsSignal, type(rhsSignal)) and isinstance(
	    rhsSignal, type(lhsSignal)
	), "Operations can only meaningfully be performed on Signals of the same type."

	if interval.getUpper() == float('inf'):
		# Unbounded until: robustness(xU[a, +inf]y) = robustness(always[0, a](xUy))
		untimedUntilResult: Signal = computeUntimedUntil(lhsSignal, rhsSignal)
		alwaysInterval: Interval = Interval(0, interval.getLower())
		output: Signal = computeTimedAlways(untimedUntilResult, alwaysInterval)
	else:
		# Bounded until: robustness(xU[a,b]y) =
		# robustness(
		# 	eventually[a,b](y) AND
		# 	(xU[a, +inf]y)
		# )
		eventuallyRhs: Signal = computeTimedEventually(rhsSignal, interval)
		unboundedInterval: Interval = Interval(interval.getLower(), float('inf'))
		unboundedUntil: Signal = computeTimedUntil(lhsSignal, rhsSignal, unboundedInterval)
		output: Signal = computeAnd(eventuallyRhs, unboundedUntil)
	output.setName('timedUntil')

	# Compute the expected timestamp set, then remove all unexpected timestamps
	offset = interval.getUpper() if interval.getUpper() != float('inf') else interval.getLower()
	times = [
	    round(x - offset, 5) for x in filter( # If x in interval [0, a[, don't include. 
	        lambda x: x >= offset and x >= interval.getLower(),
	        lhsSignal.getTimes(), # If x < 0 after subtraction, don't include. 
	    )
	]
	output.filterTimes(times)
	output.recomputeDerivatives()
	return output
