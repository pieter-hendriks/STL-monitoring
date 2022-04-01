from ..utility import Point, LineSegment
from ..signals import Signal


def __addAscendingResult(
    signal: Signal, timeIndex: int, previousResult: float, output: Signal
) -> None:
	value = max(signal.getValue(timeIndex + 1), previousResult)
	output.emplaceCheckpoint(signal.getTime(timeIndex), value, 0)


def __addLargerThanPreviousAndDescendingResult(
    signal: Signal, timeIndex: int, previousResult: float, output: Signal
) -> None:
	cp = signal.getCheckpoint(timeIndex)
	output.addCheckpoint(cp)


def __addSmallerThanPreviousResult(
    signal: Signal, timeIndex: int, previousResult: float, output: Signal
) -> None:
	output.emplaceCheckpoint(signal.getTime(timeIndex), previousResult, 0)


def __addCrossesPreviousAndDescendingResult(
    signal: Signal, timeIndex: int, previousResult: float, output: Signal
) -> None:
	constStart: Point = Point(signal.getTime(timeIndex), previousResult)
	constEnd: Point = Point(signal.getTime(timeIndex + 1), previousResult)
	resultConstSignal: LineSegment = LineSegment(constStart, constEnd)
	sigStart: Point = Point(signal.getTime(timeIndex), signal.getValue(timeIndex))
	sigEnd: Point = Point(signal.getTime(timeIndex + 1), signal.getValue(timeIndex + 1))
	signalSegment: LineSegment = LineSegment(sigStart, sigEnd)
	intersect = LineSegment.computeIntersectionPoint(resultConstSignal, signalSegment)
	output.emplaceCheckpoint(intersect.x, intersect.y, 0)
	output.addCheckpoint(signal.getCheckpoint(timeIndex))


def computeUntimedEventually(signal: Signal) -> Signal:
	""" Computes untimed eventually STL operation. Creates a new Signal instance to hold the result. """
	# For any t in domain, robustness(eventually(s)) == supremum[t' >= t](y(t'))
	# 	--> for all s < t: z(s) = max(sup[s, t[(y), z(t))
	# Step computation by applying the property at t = t{i+1} (= time of sample i+1)
	signalType = type(signal)
	output: Signal = signalType("untimedEventually")
	previousIterationResult: float = -1
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
	output.simplify()
	return output