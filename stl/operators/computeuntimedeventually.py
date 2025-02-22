""" Operation implementation for the untimed Eventually STL operation """
from ..utility import Point, LineSegment
from ..signals import Signal


def __addAscendingResult(signal: Signal, timeIndex: int, previousResult: float, output: Signal) -> None:
	value = max(signal.getValue(timeIndex + 1), previousResult)
	output.emplaceCheckpoint(signal.getTime(timeIndex), value, 0)


# pylint: disable=unused-argument
def __addLargerThanPreviousAndDescendingResult(
    signal: Signal,
    timeIndex: int,
    previousResult: float,  # type: ignore
    output: Signal
) -> None:
	output.addCheckpoint(signal.getCheckpoint(timeIndex))
# pylint: enable=unused-argument


def __addSmallerThanPreviousResult(signal: Signal, timeIndex: int, previousResult: float, output: Signal) -> None:
	output.emplaceCheckpoint(signal.getTime(timeIndex), previousResult, 0)


def __addCrossesPreviousAndDescendingResult(
    signal: Signal, timeIndex: int, previousResult: float, output: Signal
) -> None:
	output.addCheckpoint(signal.getCheckpoint(timeIndex))
	constPreviousStart: Point = Point(signal.getTime(timeIndex), previousResult)
	constPreviousEnd: Point = Point(signal.getTime(timeIndex + 1), previousResult)
	constPreviousSegment: LineSegment = LineSegment(constPreviousStart, constPreviousEnd)
	sigStart: Point = Point(signal.getTime(timeIndex), signal.getValue(timeIndex))
	sigEnd: Point = Point(signal.getTime(timeIndex + 1), signal.getValue(timeIndex + 1))
	signalSegment: LineSegment = LineSegment(sigStart, sigEnd)
	intersect = LineSegment.computeIntersectionPoint(constPreviousSegment, signalSegment)
	intersect.normalize()
	output.emplaceCheckpoint(intersect.x, intersect.y, 0)


def computeUntimedEventually(signal: Signal) -> Signal:
	""" Computes untimed eventually STL operation. Creates a new Signal instance to hold the result. """
	# For any t in domain, robustness(eventually(s)) == supremum[t' >= t](y(t'))
	# 	--> for all s < t: z(s) = max(sup[s, t[(y), z(t))
	# Step computation by applying the property at t = t{i+1} (= time of sample i+1)
	signalType = type(signal)
	output: Signal = signalType("untimedEventually")
	if signal.isEmpty():
		return output
	previousIterationResult: float = float('-inf')
	for timeIndex in reversed(range(signal.getCheckpointCount() - 1)):
		if signal.getValue(timeIndex) <= signal.getValue(timeIndex + 1):
			__addAscendingResult(signal, timeIndex, previousIterationResult, output)
		elif previousIterationResult >= signal.getValue(timeIndex) > signal.getValue(timeIndex + 1):
			__addSmallerThanPreviousResult(signal, timeIndex, previousIterationResult, output)
		elif signal.getValue(timeIndex) > signal.getValue(timeIndex + 1) >= previousIterationResult:
			__addLargerThanPreviousAndDescendingResult(signal, timeIndex, previousIterationResult, output)
		elif signal.getValue(timeIndex) > previousIterationResult > signal.getValue(timeIndex + 1):
			__addCrossesPreviousAndDescendingResult(signal, timeIndex, previousIterationResult, output)
		# Update the result for this iteration, so we can correctly use it in next.
		previousIterationResult = output.getValue(output.computeIndexForTime(signal.getTime(timeIndex)))

	# The final (limit) value is not computed by the algorithm, so we add it manually
	# The output at the last checkpoint is exactly the input, because we have no further data points.
	# The 'eventually' value is then exactly the identity function.
	output.addCheckpoint(signal.getCheckpoint(-1))

	output.recomputeDerivatives()
	return output
