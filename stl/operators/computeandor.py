from typing import Callable
from ..signals import Signal

# Implementation of AND/OR
def __andOrHelper(lhs: Signal, rhs: Signal, operator: Callable=None) -> Signal:
	""" Helper function for the computation of AND and OR, since these are very similar. Creates a new Signal instance to hold the result. """
	lhs: Signal; rhs: Signal; lhs, rhs = Signal.computeComparableSignals(lhs, rhs)
	result: Signal = Signal("andor")
	for i in range(lhs.getCheckpointCount()):
		if lhs.getValue(i) == rhs.getValue(i):
			result.addCheckpoint(lhs.getCheckpoint(i))
		else:
			if operator(lhs.getValue(i), rhs.getValue(i)):
				result.addCheckpoint(lhs.getCheckpoint(i))
			else:
				result.addCheckpoint(rhs.getCheckpoint(i))
	result.recomputeDerivatives()
	return result

def computeAnd(lhs: Signal, rhs: Signal) -> Signal:
	""" Computes the logical AND between the two Signals (quantitative). Creates a new Signal instance to hold the result.  """
	s = __andOrHelper(lhs, rhs, lambda x, y: x < y)
	# Change the name to specific operation. Probably not vital.
	s.setName("and")
	return s

def computeOr(lhs: Signal, rhs: Signal) -> Signal:
	""" Computes the logical OR between the two Signals (quantitative). Creates a new Signal instance to hold the result.  """
	s = __andOrHelper(lhs, rhs, lambda x, y: x > y)
	# Change the name to specific operation. Probably not vital.
	s.setName("or")
	return s