from ..signals import Signal
from ..utility import getSortedMergedListNoDuplicates, Interval
from typing import List

from .computeandor import computeAnd, computeOr
from .computeuntimedeventually import computeUntimedEventually


def computeUntimedUntil(lhsSignal: Signal, rhsSignal: Signal) -> Signal: 
	""" Computes untimed until STL operation. Creates a new Signal instance to hold the result. """
	assert type(lhsSignal) == type(rhsSignal), "Operations can only be meaningfully performed for Signals of the same type."
	signalType = type(lhsSignal)
	allTimes: List[float] = getSortedMergedListNoDuplicates(lhsSignal.getTimes(), rhsSignal.getTimes())
	previousValue: Signal = signalType.createConstant('previous', -1, allTimes) 
	currentIndex = lhsSignal.getCheckpointCount() - 2
	output: Signal = signalType("untimedUntil") 
	while currentIndex >= 0:
		currentInterval: Interval = Interval(lhsSignal.getTime(currentIndex), lhsSignal.getTime(currentIndex + 1))
		currentLhsInterval: Signal = lhsSignal.computeInterval(currentInterval) 
		currentRhsInterval: Signal = rhsSignal.computeInterval(currentInterval) 
		# https://link.springer.com/chapter/10.1007/978-3-642-39799-8_19
		# Implementation of Algorithm 2; slight corrections to match the section where they describe the math (Section 4, subsection 'Operatur U.', page 8)
		if lhsSignal.getDerivative(currentIndex) <= 0:
			constLhsUpper: Signal = signalType.createConstant('yconst', lhsSignal.getValue(currentIndex + 1), [currentInterval.getLower(), currentInterval.getUpper()])   # LHS(t) == OK
			previousAndConstLhsUpper: Signal = computeAnd(constLhsUpper, previousValue)   # MIN(lhs(t), z(t)) == OK
			lhsAndRhs: Signal = computeAnd(currentRhsInterval, currentLhsInterval)   # MIN(rhs(tau), lhs(tau)) == OK
			eventuallyLhsAndRhs: Signal = computeUntimedEventually(lhsAndRhs)   # SUP(MIN(rhs(tau), lhs(tau))) (==z_t(s)) == OK
			outputSegment: Signal = computeOr(eventuallyLhsAndRhs, previousAndConstLhsUpper)   # MAX(zt(s), min(LHS,OLD)) == OK
		else:
			leftConstSignal: Signal = signalType.createConstant("leftconst", lhsSignal.getValue(currentIndex), [currentInterval.getLower(), currentInterval.getUpper()])  # LHS(s) == OK
			eventuallyRhs: Signal = computeUntimedEventually(currentRhsInterval)  # SUP(rhs) == OK
			lhsAndEventuallyRhs: Signal = computeAnd(eventuallyRhs, leftConstSignal)  # MIN(SUP(RHS), LHS(s)) == OK
			#eventuallyLhsAndRhs: Signal = self.computeUntimedEventually(lhsAndRhs) # SUP(MIN(LHS, RHS)) == NOT OK! -> Should be MIN(lhs(s), SUP(rhs))
			lhsAndPrevious: Signal = computeAnd(leftConstSignal, previousValue)  # MIN(LHS, OLD) == OK
			outputSegment: Signal = computeOr(lhsAndEventuallyRhs, lhsAndPrevious)  # MAX(zt(s), min(LHS,OLD)) == OK
		for cp in outputSegment.getCheckpoints():
			if currentInterval.contains(cp.getTime(), closed=False):
				output.addCheckpoint(cp)
		previousValue = signalType.createConstant('previous', output.getValue(output.computeIndexForTime(lhsSignal.getTime(currentIndex))), allTimes)
		currentIndex -= 1
	
	# The final (limit) value is not computed by the algorithm, so we add it manually
	# x UNTIL y ==> y holds at the current (or a future) position, x holds until at least that position (exclusive)
	# Since there are no future positions, this translates to y holds at the current position, because the intersection can be exclusive.
	output.emplaceCheckpoint(lhsSignal.getTime(-1), rhsSignal.getValue(-1), 0)
	output.recomputeDerivatives()
	return output