from ..signals import Signal, SignalValue
from ..utility import Interval
from typing import List, Tuple

def computeTimedEventually(signal: Signal, interval: Interval) -> Signal: 
	"""
	Computes timed eventually STL operation. Creates a new Signal instance to hold the result. 
	Timed Eventually is the supremum of the signal over the interval. 

	Modified version of the min-max streaming filter algorithm described by Daniel Lemire in 
	STREAMING MAXIMUM-MINIMUM FILTER USING NO MORE THAN THREE COMPARISONS PER ELEMENT
	https://arxiv.org/abs/cs/0610046

	Modifications:  - Use time values rather than indices
									- Eliminate the use of L and the min-computation
									- Swap code around - extra insert before main alg instead of after
									- Remove requirement for w > 2
	"""
	signalType = type(signal)
	# Copy the signal so we don't modify the object outside of this function
	signal: Signal = signalType.fromCheckpoints('copy', signal.getCheckpoints())
	# Drop the prefix we ignore (lower bound of the interval) and shift the signal back to the same start time.
	signal = signal.computeInterval(Interval(interval.getLower() + signal.getTime(0), float('inf'))) 
	signal = signal.shift(-1 * interval.getLower())
	# Size of the interval we are keeping a maximum over. Using single variable is easier than working with an interval.
	windowWidth: float = interval.getUpper() - interval.getLower()
	# Set of potential maxima
	maximumCandidates: List[float] = []
	# Initialize the output signal
	out: Signal = signalType('timedEventually')
	# in case of empty signal, return empty signal
	if signal.isEmpty():
		return out
	# In case of Singular signal, return either a) the signal itself, in case of singular interval
	#                                           b) an empty signal, in case of non-singular interval
	if signal.isSingular():
		if windowWidth == 0:
			out.addCheckpoint(signal.getCheckpoint(0))
		return out
	# Algorithm doesn't include the first timestep if windowWidth < first segment size.
	# this bit adds that first element when necessary
	if windowWidth < signal.getTime(1) - signal.getTime(0):
		# Checkpoint 1 isn't part of the window yet, so value must be of checkpoint zero.
		out.addCheckpoint(signal.getCheckpoint(0))
		# Next extremum can be, at the earliest, at the next sample point, so the algorithm will fill in the rest of the values.
	# Iterate over all segments of the signal -- -1 because we have segment = [segmentIndex, segmentIndex+1]
	for segmentIndex in range(signal.getCheckpointCount() - 1):
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
		# Filter maximum candidates, remove values at second to last position until it's a sorted (descending) list again.
		# This occurs, at the latest, when there is one element remaining. A one-element list is always sorted, in any order.
		while len(maximumCandidates) >= 2:
			# if new candidate is larger, the previous one will never again be useful.
			if maximumCandidates[-2].getValue() < maximumCandidates[-1].getValue():
				maximumCandidates.pop(-2)
			else:
				break
		# TODO: Figure out if there's a way to do this without duplicating the conditions
		if segment[1].getTime() >= windowWidth: # Assumes signal.getTime(0) == 0, which by our shifts must be the case
			# Add to output
			# Timestamp = windowLowerBound (==segmentUpperBound - windowWidth) (e.g. for signal ([0, 10], [0, 1]) with windowSize 0.5, a sample with value 1 at timestep 9.5 must be created)
			out.emplaceCheckpoint(currentWindowLowerBound, maximumCandidates[0].getValue(), 0)
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