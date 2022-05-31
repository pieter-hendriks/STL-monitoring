""" STL untimed Always Operation """
from ..signals import Signal
from .computenot import computeNot
from .computeuntimedeventually import computeUntimedEventually


def computeUntimedAlways(signal: Signal) -> Signal:
	""" Computes the untimed always (globally) STL operation. Creates a new Signal instance to hold the result.  """

	# Alternative implementation:
	# Keep a running minimum, initialize with last checkpoint in src signal
	# Go through signal backwards, updating minimum as we go
	# For each timestep in source signal, add updated minimum to new signal at said timestep
	# Compute derivatives at the end
	#
	# Which is O(len(signal))

	# Current implementation: always(x) = not(eventually(not(x)))

	signalType = type(signal)
	notSignal: signalType = computeNot(signal)
	eventuallyNotSignal: signalType = computeUntimedEventually(notSignal)
	alwaysSignal: signalType = computeNot(eventuallyNotSignal)
	alwaysSignal.setName("untimedAlways")
	# always = not(eventually(not x))
	return alwaysSignal
