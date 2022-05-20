""" STL timed Always operation """
from ..signals import Signal
from ..utility import Interval
from .computenot import computeNot
from .computetimedeventually import computeTimedEventually


def computeTimedAlways(signal: Signal, interval: Interval) -> Signal:
	""" Computes the timed always (globally) STL operation. Creates a new Signal instance to hold the result.  """
	# always = not(eventually(not x))
	signalType = type(signal)
	notSignal: signalType = computeNot(signal)
	eventuallyNotSignal: signalType = computeTimedEventually(notSignal, interval)
	alwaysSignal: signalType = computeNot(eventuallyNotSignal)
	alwaysSignal.setName("timedAlways")

	# Compute the expected timestamp set, then remove all unexpected timestamps
	offset = interval.getUpper() if interval.getUpper() != float('inf') else interval.getLower()
	times = [
	    round(x - offset, 5) for x in filter( # If x in interval [0, a[, don't include. 
	        lambda x: x >= offset and x >= interval.getLower(),
	        signal.getTimes(), # If x < 0 after subtraction, don't include.
	    )
	]
	alwaysSignal.filterTimes(times)
	alwaysSignal.recomputeDerivatives()
	return alwaysSignal
