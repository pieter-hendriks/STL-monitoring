""" STL timed Eventually operation """
from typing import List, Tuple
from ..signals import Signal, SignalValue
from ..utility import Interval

# pylint: disable=too-many-branches
def computeTimedEventually(inSignal: Signal, interval: Interval) -> Signal:
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
	signalType = type(inSignal)
	# Initialize the output signal
	out: Signal = signalType('timedEventually')
	if inSignal.isEmpty():
		return out
	# Drop the prefix we ignore (lower bound of the interval) and shift the signal back to the same start time.
	signal = inSignal.computeInterval(Interval(interval.getLower() + inSignal.getTime(0), float('inf')))
	signal = inSignal.shift(-1 * interval.getLower())
	# Size of the interval we are keeping a maximum over. Using single variable is easier than working with an interval.
	windowWidth: float = interval.getUpper() - interval.getLower()
	# Set of potential maxima
	maximumCandidates: List[SignalValue] = []
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
		# Checkpoint 1 isn't part of the window yet, compute an initial value manually
		initialMax = max(signal.getValue(0), signal.computeInterpolatedValue(windowWidth))
		out.emplaceCheckpoint(signal.getTime(0), initialMax)
		# Earliest next extremum can be is at next sample point
		# so the algorithm will fill in the rest of the values.
	# Iterate over all segments of the signal -- -1 because we have segment = [segmentIndex, segmentIndex+1]
	for segmentIndex in range(signal.getCheckpointCount() - 1):
		segment: Tuple[SignalValue, SignalValue] = signal.getCheckpoint(segmentIndex), signal.getCheckpoint(segmentIndex + 1)
		currentWindowLowerBound: float = segment[1].getTime() - windowWidth
		currentWindowUpperBound: float = segment[1].getTime()
		# Filter the set of candidates -- if timestamp is lower than what we're currently working on, it's not useful
		while maximumCandidates:
			if maximumCandidates[0].getTime() < currentWindowLowerBound:
				maximumCandidates.pop(0)
				continue
			break
		if segment[0].getValue() >= segment[1].getValue() or segment[1].getTime() > currentWindowUpperBound:
			# Candidate is lower bound if lowerboundvalue >= upperboundvalue or if upperbound falls outside of current window.
			# Check to see if last element of candidates == current to add;
			# If it is, we've added it already and this would be silly.
			if not maximumCandidates or maximumCandidates[-1] != segment[0]:
				maximumCandidates.append(segment[0])
		else:
			# Other cases, the upper bound is the candidate (upper in window, upper > lower)
			maximumCandidates.append(segment[1])
		# Filter maximum candidates, remove values at second to last position until it's a sorted (descending) list again.
		# This occurs, at the latest, when there is one element remaining. A one-element list is always sorted.
		while len(maximumCandidates) >= 2:
			# if new candidate is larger, the previous one will never again be useful.
			if maximumCandidates[-2].getValue() < maximumCandidates[-1].getValue():
				maximumCandidates.pop(-2)
			else:
				break
		if segment[1].getTime() >= windowWidth: # Assumes signal.getTime(0) == 0, which by our shifts must be the case
			# Add to output
			# Timestamp = windowLowerBound (==segmentUpperBound - windowWidth)
			# (e.g. for signal ([0, 10], [0, 1]) with windowSize 0.5, a sample with value 1 at timestep 9.5 must be created)
			out.emplaceCheckpoint(round(currentWindowLowerBound, 5), maximumCandidates[0].getValue(), 0)
	# Compute the expected timestamp set, then remove all unexpected timestamps
	offset = interval.getUpper() if interval.getUpper() != float('inf') else interval.getLower()
	times = [
	    round(x - offset, 5) for x in filter( # If x in interval [0, a[, don't include. 
	        lambda x: x >= offset and x >= interval.getLower(),  
	        inSignal.getTimes(), # If x < 0 after subtraction, don't include. 
	    )
	]
	out.filterTimes(times)
	out.recomputeDerivatives()
	return out

# pylint: enable=too-many-branches
