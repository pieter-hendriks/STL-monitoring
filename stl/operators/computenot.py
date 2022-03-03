from ..signals import Signal
def computeNot(signal: Signal) -> Signal:
	""" Computes the STL not operation for the given Signal. This is the same as multiplying all values by -1. Creates a new Signal instance to return the result. """
	signalType = type(signal)
	output = signalType('not')
	for cp in signal.getCheckpoints():
		output.emplaceCheckpoint(cp.getTime(), cp.getValue() * -1, cp.getDerivative() * -1)
	return output