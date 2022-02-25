from typing import Callable, List
from ...utility import Interval, Point, LineSegment, getSortedMergedListNoDuplicates

# Implementation of ABS
@classmethod
def computeAbsoluteValue(cls, s: 'Signal') -> None: #type: ignore
	"""Modifies all values in s to be positive, then recomputes the derivatives to their correct values."""
	for i in range(len(s.checkpoints)):
		s.checkpoints[i].setValue(abs(s.checkpoints[i].getValue()))
	s.recomputeDerivatives()


# Implementation of AND/OR
def __andOrHelper(cls, lhs: 'Signal', rhs: 'Signal', operator: Callable=None) -> 'Signal': #type: ignore
	""" Helper function for the computation of AND and OR, since these are very similar. """
	lhs: cls; rhs: cls; lhs, rhs = cls.computeComparableSignals(lhs, rhs)
	result: cls = cls("andor")
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

@classmethod
def computeAnd(cls, lhs: 'Signal', rhs: 'Signal') -> 'Signal': #type: ignore
	""" Computes the logical AND between the two Signals (quantitative). """
	s = __andOrHelper(cls, lhs, rhs, lambda x, y: x < y)
	# Change the name to specific operation. Probably not vital.
	s.setName("and")
	return s
	
@classmethod
def computeOr(cls, lhs: 'Signal', rhs: 'Signal') -> 'Signal': #type: ignore
	""" Computes the logical OR between the two Signals (quantitative). """
	s = __andOrHelper(cls, lhs, rhs, lambda x, y: x > y)
	# Change the name to specific operation. Probably not vital.
	s.setName("or")
	return s


@classmethod
def computeNot(cls, signal: 'Signal') -> 'Signal': #type: ignore
	output = cls('not')
	for cp in signal.getCheckpoints():
		output.emplaceCheckpoint(cp.getTime(), cp.getValue() * -1, cp.getDerivative() * -1)
	return output

@classmethod
def computeTimedAlways(cls, signal: 'Signal', interval: Interval) -> 'Signal': # type: ignore
	signalType = type(signal)
	notSignal: signalType = cls.computeNot(signal) # type: ignore
	eventuallyNotSignal: signalType = cls.computeTimedEventually(notSignal, interval) # type: ignore
	alwaysSignal: signalType = cls.computeNot(eventuallyNotSignal) # type: ignore
	alwaysSignal.setName("timedAlways")
	# always = not(eventually(not x))
	return alwaysSignal

@classmethod
def computeTimedEventually(cls, signal: 'Signal', interval: Interval) -> 'Signal': # type: ignore
	"""
	Timed Eventually is the supremem of the signal over the interval.

	Modified version of the min-max streaming filter algorithm described by Daniel Lemire in 
	STREAMING MAXIMUM-MINIMUM FILTER USING NO MORE THAN THREE COMPARISONS PER ELEMENT
	https://arxiv.org/abs/cs/0610046

	Modifications:  - Use time values rather than indices
									- Eliminate the use of L and the min-computation
	"""
	# We compute this using a sliding window maximum filter - reference available in lemireMaximumAlgorithm method.
	
	# First, we preprocess the signal to better fit what the algorithm expects.
	# There's a prefix that carries no meaning for this operation; drop it
	signal = signal.computeInterval(Interval(interval.getLower() + signal.getTime(0), float('inf'))) # Logarithmic in size of the signal
	# Timestamps will have to be adjusted for the output to be correctly labelled
	signal = signal.shift(-1 * interval.getLower()) # Linear in size of the signal
	# This modifies our interval to be [0, b-a] instead of [a, b], represent it as a single value (b-a+1, to account for inclusion of 0.)
	currentIndex: int = 1
	windowWidth: float = interval.getUpper() - interval.getLower() + 1 
	cwlb: float = signal.getTime(0) # CurrentWindowUpperBound = cwub
	cwub: float = signal.getTime(currentIndex) # CurrentWindowLowerBound = cwlb
	maximumCandidates: List[float] = []
	out: 'Signal' = cls("timedEventually") # type: ignore
	# Then, we can begin the actual algorithm!
	while cwub < signal.getTime(-1): # Limit the algorithm to the times defined in the signal!
		# If we have assessed at least a window size
		if cwub - signal.getTime(0) >= windowWidth:
			# Add a checkpoint!
			time: float = cwub - windowWidth
			value: float = signal.computeInterpolatedValue(maximumCandidates[0] if maximumCandidates else cwlb)
			out.emplaceCheckpoint(time, value)
		# If, on the current window, we're ascending
		if signal.computeInterpolatedValue(cwub) > signal.computeInterpolatedValue(cwlb):
			while maximumCandidates:
				# Drop values from maximum candidates that are no longer in the running
				if signal.computeInterpolatedValue(cwub) <= signal.computeInterpolatedValue(maximumCandidates[-1]):
					if cwub == windowWidth + maximumCandidates[0]:
						maximumCandidates.pop(0)
					break
				maximumCandidates.pop(-1)
		else: # Current window descending
			maximumCandidates.append(cwlb) # Lower bound is the maximal candidate
			if cwub == windowWidth + maximumCandidates[0]:
				maximumCandidates.pop(0)
		# Update values for the next iteration
		currentIndex += 1
		cwlb = cwub
		cwub = signal.getTime(currentIndex)
	# Add the final element computed by the algorithm.
	time = signal.getTime(-1) - windowWidth
	value = signal.computeInterpolatedValue(maximumCandidates[0] if maximumCandidates else signal.getTime(-2))
	out.emplaceCheckpoint(time, value)

	# Add the limit element that falls out of scope of the algorithm.
	lastSampleTime: float = cwub - windowWidth + 1
	lastSampleInterval: Interval = Interval(lastSampleTime, cwub)
	lastSampleValueInterval: List[float] = signal.computeInterval(lastSampleInterval).getValues()
	# The value of eventually for a specific interval is the maximal in that interval
	# For a single interval, we can compute that trivially without impacting the runtime at all 
	# (window size <= signal size, so O(s + w) <= O(2s) == O(s))
	# If this assumption doesn't hold, we can shortcircuit to O(1), since the result will be the empty signal.
	lastSampleValue: float = max(lastSampleValueInterval)
	out.emplaceCheckpoint(lastSampleTime, lastSampleValue)
	out.recomputeDerivatives()
	return out

@classmethod
def computeTimedUntil(cls, lhsSignal: 'Signal', rhsSignal: 'Signal', interval: Interval) -> 'Signal': # type: ignore
	if interval.getUpper() == float('inf'):
		# Unbounded until: robustness(xU[a, +inf]y) = robustness(always[0, a](xUy))
		untimedUntilResult: 'Signal' = cls.computeUntimedUntil(lhsSignal, rhsSignal) # type: ignore
		alwaysInterval: Interval = Interval(0, interval.getLower())
		output: 'Signal' = cls.computeTimedAlways(untimedUntilResult, alwaysInterval) # type: ignore
	else:
		# Bounded until: robustness(xU[a,b]y) = robustness(eventually[a,b](y)ANDxU[a,+inf]y)
		eventuallyRhs: 'Signal' = cls.computeTimedEventually(rhsSignal, interval) # type: ignore
		unboundedInterval: Interval = Interval(interval.getLower(), float('inf'))
		unboundedUntil: 'Signal' = cls.computeTimedUntil(lhsSignal, rhsSignal, unboundedInterval) # type: ignore
		output: 'Signal' = cls.computeAnd(eventuallyRhs, unboundedUntil) # type: ignore
	output.setName('timedUntil')
	return output



def addAscendingResult(signal: 'Signal', timeIndex: int, previousResult: float, output: 'Signal') -> None: # type: ignore
	value = max(signal.getValue(timeIndex + 1), previousResult)
	output.emplaceCheckpoint(signal.getTime(timeIndex), value, 0)

def addLargerThanPreviousDescendingResult(signal: 'Signal', timeIndex: int, previousResult: float, output: 'Signal') -> None: # type: ignore
	cp = signal.getCheckpoint(timeIndex)
	output.addCheckpoint(cp)

def addSmallerThanPreviousResult(signal: 'Signal', timeIndex: int, previousResult: float, output: 'Signal') -> None: # type: ignore
	output.emplaceCheckpoint(signal.getTime(timeIndex), previousResult, 0)

def addCrossesPreviousDescendingResult(signal: 'Signal', timeIndex: int, previousResult: float, output: 'Signal') -> None: # type: ignore
	constStart: Point = Point(signal.getTime(timeIndex), previousResult)
	constEnd: Point = Point(signal.getTime(timeIndex + 1), previousResult)
	resultConstSignal: LineSegment = LineSegment(constStart, constEnd)
	sigStart: Point = Point(signal.getTime(timeIndex), signal.getValue(timeIndex))
	sigEnd: Point = Point(signal.getTime(timeIndex+1), signal.getValue(timeIndex+1))
	signalSegment: LineSegment = LineSegment(sigStart, sigEnd)
	intersect = LineSegment.computeIntersectionPoint(resultConstSignal, signalSegment)
	output.emplaceCheckpoint(intersect.x, intersect.y, 0)
	output.addCheckpoint(signal.getCheckpoint(timeIndex))

@classmethod
def computeUntimedEventually(cls, signal: 'Signal') -> 'Signal': # type: ignore
	# For any t in domain, robustness(eventually(s)) == supremum[t' >= t](y(t'))
	# 	--> for all s < t: z(s) = max(sup[s, t[(y), z(t))
	# Step computation by applying the property at t = t{i+1} (= time of sample i+1)
	output: 'Signal' = cls("untimedEventually") # type: ignore
	previousIterationResult: float = -1 
	for timeIndex in reversed(range(signal.getCheckpointCount() - 1)):
		if signal.getValue(timeIndex) <= signal.getValue(timeIndex + 1):
			addAscendingResult(signal, timeIndex, previousIterationResult, output)
		elif previousIterationResult >= signal.getValue(timeIndex) > signal.getValue(timeIndex + 1):
			addSmallerThanPreviousResult(signal, timeIndex, previousIterationResult, output)
		elif signal.getValue(timeIndex) > signal.getValue(timeIndex + 1) >= previousIterationResult:
			addLargerThanPreviousDescendingResult(signal, timeIndex, previousIterationResult, output)
		elif signal.getValue(timeIndex) > previousIterationResult > signal.getValue(timeIndex + 1):
			addCrossesPreviousDescendingResult(signal, timeIndex, previousIterationResult, output)
		# Update the result for this iteration, so we can correctly use it in next.
		previousIterationResult = output.getValue(output.computeIndexForTime(signal.getTime(timeIndex)))

	# The final (limit) value is not computed by the algorithm, so we add it manually
	# The output at the last checkpoint is exactly the input, because we have no further data points.
	# The 'eventually' value is then exactly the identity function.
	output.addCheckpoint(signal.getCheckpoint(-1))
	output.recomputeDerivatives()
	return output

@classmethod
def computeUntimedUntil(cls, lhsSignal: 'Signal', rhsSignal: 'Signal') -> 'Signal': # type: ignore
	allTimes: List[float] = getSortedMergedListNoDuplicates(lhsSignal.getTimes(), rhsSignal.getTimes())
	previousValue: 'Signal' = cls.createConstant('previous', -1, allTimes) # type: ignore
	currentIndex = lhsSignal.getCheckpointCount() - 2
	output: 'Signal' = cls("untimedUntil") # type: ignore
	while currentIndex >= 0:
		currentInterval: Interval = Interval(lhsSignal.getTime(currentIndex), lhsSignal.getTime(currentIndex + 1))
		currentLhsInterval: 'Signal' = lhsSignal.computeInterval(currentInterval) # type: ignore
		currentRhsInterval: 'Signal' = rhsSignal.computeInterval(currentInterval) # type: ignore
		# https://link.springer.com/chapter/10.1007/978-3-642-39799-8_19
		# Implementation of Algorithm 2; slight corrections to match the section where they describe the math (Section 4, subsection 'Operatur U.', page 8)
		if lhsSignal.getDerivative(currentIndex) <= 0:
			constLhsUpper: 'Signal' = cls.createConstant('yconst', lhsSignal.getValue(currentIndex + 1), [currentInterval.getLower(), currentInterval.getUpper()])  # type: ignore # LHS(t) == OK
			previousAndConstLhsUpper: 'Signal' = cls.computeAnd(constLhsUpper, previousValue)  # type: ignore # MIN(lhs(t), z(t)) == OK
			lhsAndRhs: 'Signal' = cls.computeAnd(currentRhsInterval, currentLhsInterval)  # type: ignore # MIN(rhs(tau), lhs(tau)) == OK
			eventuallyLhsAndRhs: 'Signal' = cls.computeUntimedEventually(lhsAndRhs)  # type: ignore # SUP(MIN(rhs(tau), lhs(tau))) (==z_t(s)) == OK
			outputSegment: 'Signal' = cls.computeOr(eventuallyLhsAndRhs, previousAndConstLhsUpper)  # type: ignore # MAX(zt(s), min(LHS,OLD)) == OK
		else:
			leftConstSignal: 'Signal' = cls.createConstant("leftconst", lhsSignal.getValue(currentIndex), [currentInterval.getLower(), currentInterval.getUpper()]) # type: ignore # LHS(s) == OK
			eventuallyRhs: 'Signal' = cls.computeUntimedEventually(currentRhsInterval) # type: ignore # SUP(rhs) == OK
			lhsAndEventuallyRhs: 'Signal' = cls.computeAnd(eventuallyRhs, leftConstSignal) # type: ignore # MIN(SUP(RHS), LHS(s)) == OK
			#eventuallyLhsAndRhs: Signal = self.computeUntimedEventually(lhsAndRhs) # SUP(MIN(LHS, RHS)) == NOT OK! -> Should be MIN(lhs(s), SUP(rhs))
			lhsAndPrevious: 'Signal' = cls.computeAnd(leftConstSignal, previousValue) # type: ignore # MIN(LHS, OLD) == OK
			outputSegment: 'Signal' = cls.computeOr(lhsAndEventuallyRhs, lhsAndPrevious) # type: ignore # MAX(zt(s), min(LHS,OLD)) == OK
		for cp in outputSegment.getCheckpoints():
			if currentInterval.contains(cp.getTime(), closed=False):
				output.addCheckpoint(cp)
		previousValue = cls.createConstant('previous', output.getValue(output.computeIndexForTime(lhsSignal.getTime(currentIndex))), allTimes)
		currentIndex -= 1
	
	# The final (limit) value is not computed by the algorithm, so we add it manually
	# x UNTIL y ==> y holds at the current (or a future) position, x holds until at least that position (exclusive)
	# Since there are no future positions, this translates to y holds at the current position, because the intersection can be exclusive.
	output.emplaceCheckpoint(lhsSignal.getTime(-1), rhsSignal.getValue(-1), 0)
	output.recomputeDerivatives()
	return output