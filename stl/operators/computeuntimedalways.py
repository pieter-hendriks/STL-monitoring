""" STL untimed Always Operation """
from ..signals import Signal
from .computenot import computeNot
from .computeuntimedeventually import computeUntimedEventually


def computeUntimedAlways(signal: Signal) -> Signal:
	""" Computes the untimed always (globally) STL operation. Creates a new Signal instance to hold the result.  """

	# Naive implementation (which probably performs worse)
	# Keep a running minimum, initialize with last checkpoint in src signal
	# Go through signal backwards, updating minimum as we go
	# For each timestep in source signal, add updated minimum to new signal at said timestep
	# Compute derivatives at the end
	#
	# Which is O(len(signal))

	# For now, we keep this implementation because it mirrors the timed implementation;
	# it is guaranteed to be error-free as long as the not and eventually operators are

	signalType = type(signal)
	notSignal: signalType = computeNot(signal)
	eventuallyNotSignal: signalType = computeUntimedEventually(notSignal)
	alwaysSignal: signalType = computeNot(eventuallyNotSignal)
	alwaysSignal.setName("untimedAlways")
	assert signal.getTimes() == alwaysSignal.getTimes(), 'Unexpected times mismatch in untimedalways'
	# always = not(eventually(not x))
	return alwaysSignal
