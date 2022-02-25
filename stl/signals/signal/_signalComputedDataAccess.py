from ..signalvalue import SignalValue
import warnings
from ...utility import Interval, LineSegment, Point
from typing import List

def computeInterpolatedCheckpoint(self, t: float) -> SignalValue:
	"""Compute an interpolated checkpoint for the specified time"""
	return SignalValue(t, self.computeInterpolatedValue(t), self.computeInterpolatedDerivative(t))

# Get the value of a signal at time step t
def computeInterpolatedValue(self, t: float) -> float:
	"""Compute an interpolated value for the specified time"""
	ret: float = None
	# Mirror Efficient Robustness paper implementation: 
	# A signal value outside of the defined range of the Signal is equal to 0.
	if not self.getDefinedTimeInterval().contains(t, closed=True):
		return 0
	i = 0
	# If it's within known values, find the correct time step
	while self.getTime(i) < t:
		i += 1
	if i == 0 or self.getTime(i) == t:
		# If point before signal started, return first data point
		# If it's an exact data point in the signal, return corresponding value
		ret =  self.getValue(i)
	elif i >= self.getCheckpointCount():
		# If it's after the end of signal, return last data point
		ret =  self.getValue(-1)
	else:
		# If it's somewhere between two data points, interpolate
		value = self.getValue(i - 1)
		value += (self.getValue(i) - self.getValue(i-1)) / ((self.getTime(i) - self.getTime(i-1)) * t - self.getTime(i-1))
		ret = value	# Get the value of a signal at time step t
	return ret

# Get a derivative of the signal at time step t
def computeInterpolatedDerivative(self, t: float) -> float:
	"""Compute an interpolated derivative for the specified time.\n
	Following the finite, piecewise, linear, continuous hypothesis, 
	this returns the derivative between the values (in self.getTimes()) that t is located between."""
	if t < self.getTime(0):
		warnings.warn("Got derivative before start of signal.")
		return 0
	if t > self.getTime(-1):
		return self.getDerivative(-1)
	for i in range(self.getCheckpointCount()):
		if t <= self.getTime(i):
			# Signal is linearly interpolated between points, so derivative is constant on the interval [i-1, i)
			return self.getDerivative(i-1)


def computeInterval(self, interval: Interval, half_open: bool = False) -> 'Signal': #type: ignore
	""" Find the part of the signal that fits within the specified interval (endpoint inclusion based on value of 'half_open') """
	constructedSignalName = f"{self.getName()}_interval"
	signalType = type(self)
	output: 'Signal' = signalType(constructedSignalName) # type: ignore (Unsupported annotation)
	# Handle cases where lower bound is larger or equal to biggest values in the Signal.
	if interval.getLower() > self.getLargestTime():
		return output
	elif interval.getLower() == self.getLargestTime():
		output.addCheckpoint(self.checkpoints[-1])
		return output
	# Consider trivial interval case:
	if interval.getUpper() == interval.getLower():
		if not half_open:
			output.addCheckpoint(self.computeInterpolatedCheckpoint(interval.getLower()))
		return output
	# A valid index in the Signal, where timestamp is as close as possible to (but never smaller than) the lower bound of the interval
	lowerBoundIndex = self.computeIndexForSmallestTimeAfter(interval.getLower(), inclusive=True)
	# A valid index in the Signal, where timestamp is as close as possible to (but never larger than or equal to) the upper bound of the interval
	upperBoundIndex = self.computeIndexForLargestTimeBefore(interval.getUpper(), not half_open)

	# Get the output Signal. It might be missing up to two values still: one at interval.getLower() and one at interval.getUpper()
	output = self.fromCheckpoints(constructedSignalName, self.checkpoints[lowerBoundIndex: upperBoundIndex + 1])
	if interval.getLower() not in self.getTimes() and interval.getLower() > self.getTime(0):
		# If lower bound of the interval isn't included, and does fall within our defined range, compute it
		output.addCheckpoint(self.computeInterpolatedCheckpoint(interval.getLower()))
	if not half_open and interval.getUpper() not in self.getTimes() and interval.getUpper() < self.getTime(-1):
		# If upper bound of the interval isn't included, should be, and falls within our defined range, compute it
		output.addCheckpoint(self.computeInterpolatedCheckpoint(interval.getUpper()))
	return output

def computeIndexForTime(self, time: float) -> int:
	""" Find the index where 'time' is located. Errors if time not in the current checkpoint list. """
	assert time in self.getTimes(), "Can't find an index for a time that isn't in our list."
	# Only the key element (time) matters for lookup
	return self.checkpoints.bisect_left(SignalValue(time, 0, 0))

def computeLargestTimeBefore(self, time: float, inclusive: bool = True) -> float:
	""" Return the largest timestamp (specified in a checkpoint), smaller than (or equal to, if inclusive is True) the value in the parameter"""
	if inclusive:
		compare = lambda x, y: x <= y
	else:
		compare = lambda x, y: x < y
	# Iterate over all checkpoints, reverse order
	for i in reversed(range(len(self.checkpoints))):
		cp = self.checkpoints[i]
		if compare(cp.getTime(), time):
			# If checkpoint time <= currentTime, we have the largest time before currentTime
			# Because we are going through the cp times in descending order
			return cp.getTime()
	raise RuntimeError(f"Failed to find largestTimeBefore({time}) for {self}")

def computeIndexForSmallestTimeAfter(self, time: float, inclusive: bool = True) -> int:
	""" Return the index at which the checkpoint with the timestamp closest to (but always larger than (or eq iff inclusive)) the given time is """
	smallestTimeAfter = self.computeSmallestTimeAfter(time, inclusive)
	return self.checkpoints.bisect_left(SignalValue(smallestTimeAfter, 0, 0))

def computeIndexForLargestTimeBefore(self, time: float, inclusive: bool = True) -> int:
	""" Return the index at which the checkpoint with the timestamp closest to (but always smaller than (or eq iff inclusive)) the given time is """
	largestTimeBefore = self.computeLargestTimeBefore(time, inclusive)
	return self.checkpoints.bisect_left(SignalValue(largestTimeBefore, 0, 0))

def computeSmallestTimeAfter(self, time: float, inclusive: bool = True) -> float:
	"""Get the smallest time (that is specified in a checkpoint) that is larger than (or equal to, if inclusive is True) the value in parameter"""
	if inclusive:
		compare = lambda x, y: x >= y
	else:
		compare = lambda x, y: x > y
	# This method assumes the times are sorted in ascending order
	for cp in self.checkpoints:
		if compare(cp.getTime(), time):
			# We're going through times in ascending order, so this is the smallest cptime after currentTime
			return cp.getTime()
	raise RuntimeError(f"Failed to find smallestTimeAfter({time}) for {self}")

def oldFormat(self) -> List[List[float]]:
	"""Grab representation of this signal in the format used in old version of the code.\nMay be useful to compare outputs between the versions."""
	# Might be useful sometime. 
	return [self.getTimes(), self.getValues(), self.getDerivatives()]

def computeLines(self) -> List[LineSegment]:
	ret: List[LineSegment] = []
	for i in range(self.getCheckpointCount() - 1):
		cpA: SignalValue = self.getCheckpoint(i)
		cpB: SignalValue = self.getCheckpoint(i+1)
		ret.append(LineSegment(Point(cpA.getTime(), cpA.getValue()), Point(cpB.getTime(), cpB.getValue())))
	return ret