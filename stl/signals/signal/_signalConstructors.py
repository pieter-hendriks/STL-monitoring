from typing import List, Tuple
from sortedcontainers import SortedList
from ..signalvalue import SignalValue
from ...utility import Point, Interval, LineSegment
import math
import warnings

def __init__(self, name: str = None, times: List[float] = None, values: List[float] = None, derivatives: List[float] = None):
	if name is not None and type(name) != str:
		raise RuntimeError(f"Name argument is {type(name)} (value = {name}) instead of str")
	if all([name is None, times is None, values is None, derivatives is None]):
		self.name = "defaultname"
		self.checkpoints: SortedList[SignalValue] = SortedList([], key = lambda x: x.getTime()) # type: ignore
	else:
		if times is not None:
			assert values is not None, "We can't autocompute values."
			assert all([times[i] != times[i+1] for i in range(len(times) - 1)]), "debug assert: times mustn't be equal"
		elif values is not None:
			assert False, "DEBUG STATEMENT: May need to autogenerate timestamps here."
		self.name: str = name # type: ignore
		if derivatives is None and times is not None:
			warnings.warn("Signal is autocomputing derivatives!")
			derivatives = [(values[i] + values[i+1]) / (times[i+1] - times[i]) for i in range(len(times) - 1)] + [0]
		if times is None:
			times = []
		if values is None:
			values = []
		if derivatives is None:
			derivatives = []
		self.checkpoints: SortedList[SignalValue] = SortedList([SignalValue(x, y, d) for x, y, d in zip(times, values, derivatives)], key = lambda x: x.getTime()) # type: ignore

@classmethod
def createConstant(cls, name: str, value: float, timestamps: List[float]) -> 'Signal': # type: ignore (Unsupported annotation)
	""" Create a constant Signal. """
	s = cls(name, timestamps, [value] * len(timestamps), [0] * len(timestamps))
	return s

@classmethod
def fromBooleanSignal(cls, s: 'BooleanSignal') -> 'Signal': # type: ignore (Unsupported annotation)
	""" Conversion from a Boolean Signal. """
	if not s.checkpoints:
		return cls(s.getName())
	times, values, derivatives = zip(*[(cp.getTime(), cp.getValue(), cp.getDerivative()) for cp in s.checkpoints])
	# Drop the derivatives, BooleanSignal doesn't use those.
	newSignal = cls(s.getName(), times, values, derivatives)
	newSignal.recomputeDerivatives()
	return newSignal

@classmethod
def fromCheckpoints(cls, name: str, checkpoints: List[SignalValue]) -> 'Signal': # type: ignore (Unsupported annotation)
	""" Constructs a Signal instance from a list of checkpoints. Useful for copying. """
	s = cls(name)
	s.checkpoints = SortedList(checkpoints, key=lambda x: x.getTime())
	return s

def __computeCheckpointsForComparableSignal(cls, lhsSignal: 'Signal', rhsSignal: 'Signal') -> Tuple['Signal', 'Signal']: # type: ignore
	""" Gets the checkpoints (sample points) with timestamps from both Signals when they are both defined. """
	warnings.warn("computeCheckpointsForComparableSignals docstring is out of date.")
	lhsResult: Signal = cls("lhs"); rhsResult: Signal = cls('rhs') # type: ignore
	cp: SignalValue
	bothDefinedInterval: Interval = Interval.computeIntersection(lhsSignal.getDefinedTimeInterval(), rhsSignal.getDefinedTimeInterval())
	for cp in lhsSignal.getCheckpoints():
		if bothDefinedInterval.contains(cp.getTime()):
			lhsResult.addCheckpoint(cp)
			rhsResult.emplaceCheckpoint(cp.getTime(), rhsSignal.computeInterpolatedValue(cp.getTime()), rhsSignal.computeInterpolatedDerivative(cp.getTime()))
	for cp in rhsSignal.getCheckpoints():
		# Avoid double entries by checking if the given time is already in the result.
		if bothDefinedInterval.contains(cp.getTime()) and cp.getTime() not in rhsResult.getTimes():
			rhsResult.addCheckpoint(cp)
			lhsResult.emplaceCheckpoint(cp.getTime(), lhsSignal.computeInterpolatedValue(cp.getTime()), lhsSignal.computeInterpolatedDerivative(cp.getTime()))
	return lhsResult, rhsResult

@classmethod
def computeComparableSignals(cls, lhsSignal: 'Signal', rhsSignal: 'Signal') -> List['Signal']: # type: ignore
	""" Create Signals that are comparable - this requires both Signals having the same sample point timings.\n
	First, we take all sample points from both Signals where the time values are identical.\n
	Second, we compute all points where, based on the derivative, the Signals intersect. \n
	Returns two Signals with an equal amount of sample points, where the time part of each sample point pair is equal."""

	# Get the sampling points where self and other are a) both defined or b) intersect
	# So, any time x where x in self.times() and x in other.times()
	# + any time y where, through the derivatives, we know that self.value(x) == other.value(x), assuming interpolation.
	assert type(lhsSignal) == type(rhsSignal), "Operation is unsupported between signals of different semantics."
	cls = type(lhsSignal)
	lhsResult: Signal = cls('empty'); rhsResult: Signal = cls('empty') # type: ignore
	if lhsSignal.isEmpty() or rhsSignal.isEmpty():
		return [lhsResult, rhsResult]
	# We build the sequence (ri)i≤nz containing the sampling points of y and y' when they are both defined, and the points where y and y' punctually intersect
	# First, we get the sampling points from the signals where they are both defined (i.e. all sample points with t1==t2)
	lhsResult, rhsResult = __computeCheckpointsForComparableSignal(cls, lhsSignal, rhsSignal)
	# Second, we get the intersection points
	if not lhsResult.isEmpty() and not rhsResult.isEmpty():
		lhsLines: List[LineSegment] = lhsResult.computeLines()
		rhsLines: List[LineSegment] = rhsResult.computeLines()
		intersectPoints: List[Point] = LineSegment.computeIntersectionPoints(lhsLines, rhsLines)
		for point in intersectPoints:
			if point.x not in lhsResult.getTimes():
				lhsResult.emplaceCheckpoint(point.x, point.y, 0)
				rhsResult.emplaceCheckpoint(point.x, point.y, 0)
			else:
				assert math.isclose(lhsResult.getValue(lhsResult.computeIndexForTime(point.x)), point.y, rel_tol=1e-7), "Attempted to insert a duplicate point, with different values."
				assert math.isclose(rhsResult.getValue(rhsResult.computeIndexForTime(point.x)), point.y, rel_tol=1e-7), "Attempted to insert a duplicate point, with different values."
	lhsResult.recomputeDerivatives()
	rhsResult.recomputeDerivatives()
	assert lhsResult.getTimes() == rhsResult.getTimes(), "The punctual intersection function must return two Signals with exactly equal time checkpoints."
	return [lhsResult, rhsResult]
