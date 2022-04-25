""" STL Timed Until operation """
from ..utility import Interval
from ..signals import Signal
from .computeandor import computeAnd
from .computetimedeventually import computeTimedEventually
from .computetimedalways import computeTimedAlways
from .computeuntimeduntil import computeUntimedUntil


def computeTimedUntil(lhsSignal: Signal, rhsSignal: Signal, interval: Interval) -> Signal:
	""" Computes the timed until STL operation. Creates a new Signal instance to hold the result.  """
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
	return output
