""" STL timed Always operation """
from ..signals import Signal
from ..utility import Interval
from .computenot import computeNot
from .computetimedeventually import computeTimedEventually


def computeTimedAlways(signal: Signal, interval: Interval) -> Signal:
	""" Computes the timed always (globally) STL operation. Creates a new Signal instance to hold the result.  """
	signalType = type(signal)
	notSignal: signalType = computeNot(signal)
	eventuallyNotSignal: signalType = computeTimedEventually(notSignal, interval)
	alwaysSignal: signalType = computeNot(eventuallyNotSignal)
	alwaysSignal.setName("timedAlways")
	# always = not(eventually(not x))
	return alwaysSignal
