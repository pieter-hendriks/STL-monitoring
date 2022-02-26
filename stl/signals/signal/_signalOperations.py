from typing import Callable, List, Tuple

from numpy import maximum
from ...utility import Interval, Point, LineSegment, getSortedMergedListNoDuplicates
from ..signalvalue import SignalValue

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
	Timed Eventually is the supremum of the signal over the interval.

	Modified version of the min-max streaming filter algorithm described by Daniel Lemire in 
	STREAMING MAXIMUM-MINIMUM FILTER USING NO MORE THAN THREE COMPARISONS PER ELEMENT
	https://arxiv.org/abs/cs/0610046

	Modifications:  - Use time values rather than indices
									- Eliminate the use of L and the min-computation
									- Swap code order to remove additional append at end of iterations
									- Remove requirement for w > 2 by never allowing M to be emptied
	"""
	# Copy the signal so we don't modify the object outside of this function
	signal: 'Signal' = cls.fromCheckpoints('copy', signal.getCheckpoints()) # type: ignore
	# Drop the prefix we ignore (lower bound of the interval) and shift the signal back to the same start time.
	signal.computeInterval(Interval(interval.getLower() + signal.getTime(0), float('inf'))) 
	signal.shift(-1 * interval.getLower())

	# Size of the interval we are keeping a maximum over. Using single variable is easier than working with an interval.
	windowWidth: float = interval.getUpper() - interval.getLower()
	# Set of potential maxima
	maximumCandidates: List[float] = []
	# Initialize the indices
	segmentIndex: int = 0
	out: 'Signal' = cls('timedEventually') # type: ignore
	# Iterate over all segments of the signal -- -1 because we have segment = [segmentIndex, segmentIndex+1]
	while segmentIndex < signal.getCheckpointCount() - 1:
		segment: Tuple[SignalValue, SignalValue] = signal.getCheckpoint(segmentIndex), signal.getCheckpoint(segmentIndex + 1)
		currentWindowLowerBound: float = segment[1].getTime() - windowWidth
		currentWindowUpperBound: float = segment[1].getTime()
		# Filter the set of candidates -- if timestamp is lower than what we're currently working on, it's not useful
		while maximumCandidates:
			if maximumCandidates[0].getTime() < currentWindowLowerBound:
				maximumCandidates.pop(0)
			else:
				break
		if segment[0].getValue() >= segment[1].getValue() or segment[1].getTime() > currentWindowUpperBound:
			# Candidate is lower bound if lowerboundvalue >= upperboundvalue or if upperbound falls outside of current window.
			maximumCandidates.append(segment[0])
		else:
			# Other cases, the upper bound is the candidate (i.e. upperbound falls within window and is larger than lowerbound value)
			maximumCandidates.append(segment[1])
		# Filter maximum candidates, remove values at second to last position until it's a sorted list again.
		while len(maximumCandidates) >= 2:
			# if new candidate is larger, the previous one will never again be useful.
			if maximumCandidates[-2].getValue() < maximumCandidates[-1].getValue():
				maximumCandidates.pop(-2)
			else:
				break
		# TODO: Figure out if there's a way to do this without duplicating the conditions
		if segment[1].getTime() >= windowWidth: # Assumes signal.getTime(0) == 0, which by our shifts must be the case
			# Add to output
			# Timestamp = upperbound - windowWidth (e.g. for signal ([0, 10], [0, 1]) with windowSize 0.5, a sample with value 1 at timestep 9.5 must be created)
			out.emplaceCheckpoint(segment[1].getTime() - windowWidth, maximumCandidates[0].getValue(), 0)
		# Increment index
		segmentIndex += 1
	out.recomputeDerivatives()
	return out
	# """
	# Timed Eventually is the supremum of the signal over the interval.

	# Modified version of the min-max streaming filter algorithm described by Daniel Lemire in 
	# STREAMING MAXIMUM-MINIMUM FILTER USING NO MORE THAN THREE COMPARISONS PER ELEMENT
	# https://arxiv.org/abs/cs/0610046

	# Modifications:  - Use time values rather than indices
	# 								- Eliminate the use of L and the min-computation
	# """
	# # We compute this using a sliding window maximum filter - reference available in lemireMaximumAlgorithm method.
	
	# # Short-circuit trivial case
	# if interval.getUpper() == interval.getLower(): # Empty interval means we only ever consider timestep x, so best value to return is y(x), meaning signal is unchanged.
	# 	return cls.fromCheckpoints('timedEventually', signal.getCheckpoints())

	# # First, we preprocess the signal to better fit what the algorithm expects.
	# # If there's a prefix that carries no meaning for this operation, drop it
	# signal = signal.computeInterval(Interval(interval.getLower() + signal.getTime(0), float('inf'))) # Logarithmic in size of the signal
	# # Timestamps will have to be adjusted for the output to be correctly labelled
	# signal = signal.shift(-1 * interval.getLower()) # Linear in size of the signal
	# # This modifies our interval to be [0, b-a] instead of [a, b], represent it as a single value (b-a)=windowWidth
	# currentIndex: int = 1
	# windowWidth: float = interval.getUpper() - interval.getLower()
	# # Algorithm checks segment by segment for maxima
	# # Per FPLC assumption, extrema must be a sample value in the signal. 
	# maximumCandidates: List[float] = []
	# out: 'Signal' = cls("timedEventually") # type: ignore
	# # Then, we can begin the actual algorithm!
	# while currentIndex < signal.getCheckpointCount(): # Limit the algorithm to the times defined in the signal!
	# 	cslb: float = signal.getTime(currentIndex - 1) # CurrentSegmentLowerBound = cslb
	# 	csub: float = signal.getTime(currentIndex) # CurrentSegmentUpperBound = csub

	# 	# If we have assessed at least a window size
	# 	if csub - signal.getTime(0) >= windowWidth:
	# 		# Add a checkpoint!
	# 		time: float = csub - windowWidth
	# 		value: float = signal.computeInterpolatedValue(maximumCandidates[0] if maximumCandidates else cslb)
	# 		out.emplaceCheckpoint(time, value)
	# 	# If, on the current window, we're ascending
	# 	if signal.computeInterpolatedValue(csub) > signal.computeInterpolatedValue(cslb):
	# 		while maximumCandidates:
	# 			# Drop values from maximum candidates that are no longer in the running
	# 			if signal.computeInterpolatedValue(csub) <= signal.computeInterpolatedValue(maximumCandidates[-1]):
	# 				if csub == windowWidth + maximumCandidates[0]:
	# 					maximumCandidates.pop(0)
	# 				break
	# 			maximumCandidates.pop(-1)
	# 	else: # Current window descending
	# 		maximumCandidates.append(cslb) # Lower bound is the maximal candidate
	# 		if csub == windowWidth + maximumCandidates[0]:
	# 			maximumCandidates.pop(0)
	# 	# Update values for the next iteration
	# 	currentIndex += 1
	# # Add the final element computed by the algorithm.
	# time = signal.getTime(-1) - windowWidth
	# value = signal.computeInterpolatedValue(maximumCandidates[0] if maximumCandidates else signal.getTime(-2))
	# out.emplaceCheckpoint(time, value)

	# # Add the limit element that falls out of scope of the algorithm.
	# # lastSampleTime: float = csub - windowWidth + 1
	# # lastSampleInterval: Interval = Interval(lastSampleTime, csub)
	# # lastSampleValueInterval: List[float] = signal.computeInterval(lastSampleInterval).getValues()
	# # # The value of eventually for a specific interval is the maximal in that interval
	# # # For a single interval, we can compute that trivially without impacting the runtime at all 
	# # # (window size <= signal size, so O(s + w) <= O(2s) == O(s))
	# # # If this assumption doesn't hold, we can shortcircuit to O(1), since the result will be the empty signal.
	# # lastSampleValue: float = max(lastSampleValueInterval)
	# # out.emplaceCheckpoint(lastSampleTime, lastSampleValue)
	# out.recomputeDerivatives()
	# return out

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