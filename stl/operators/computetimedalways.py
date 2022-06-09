""" STL timed Always operation """
from ..signals import Signal
from ..utility import Interval
from .computenot import computeNot
from .computetimedeventually import computeTimedEventually


def computeTimedAlways(signal: Signal, interval: Interval) -> Signal:
	""" Computes the timed always (globally) STL operation. Creates a new Signal instance to hold the result.  """
	# always = not(eventually(not x))
	notSignal: Signal = computeNot(signal)
	eventuallyNotSignal: Signal = computeTimedEventually(notSignal, interval)
	alwaysSignal: Signal = computeNot(eventuallyNotSignal)
	alwaysSignal.setName("timedAlways")
	alwaysSignal.recomputeDerivatives()
	return alwaysSignal
