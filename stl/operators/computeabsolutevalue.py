from ..signals import Signal

# Implementation of ABS
def computeAbsoluteValue(s: Signal) -> Signal:
	"""Modifies all values in s to be positive, then recomputes the derivatives to their correct values."""
	outSignal: Signal = Signal('absolutevalue')
	for cp in s.getCheckpoints():
		# Derivatives are 0, because we need to recompute them.
		outSignal.emplaceCheckpoint(cp.getTime(), abs(cp.getValue()), 0)
	outSignal.recomputeDerivatives()
	return outSignal
