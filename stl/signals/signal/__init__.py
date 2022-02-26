class Signal:
	from ._signalConstructors import __init__, createConstant, fromBooleanSignal, fromCheckpoints, computeComparableSignals
	
	from ._signalSimpleDataAccess import getName, setName, getValue, setValue, getTime, getDerivative, setDerivative
	from ._signalSimpleDataAccess import getValues, getTimes, getDerivatives
	from ._signalSimpleDataAccess import addCheckpoint, emplaceCheckpoint, getCheckpoint, getCheckpoints, getCheckpointCount
	from ._signalSimpleDataAccess import getDefinedTimeInterval, getLargestTime, popCheckpoint, isEmpty, isSingular

	from ._signalComputedDataAccess import computeInterpolatedCheckpoint, computeInterpolatedDerivative, computeInterpolatedValue
	from ._signalComputedDataAccess import computeIndexForLargestTimeBefore, computeIndexForSmallestTimeAfter, computeSmallestTimeAfter, computeLargestTimeBefore
	from ._signalComputedDataAccess import computeIndexForTime, computeInterval, oldFormat, computeLines


	from ._signalModifications import shift, merge, recomputeDerivatives

	from ._signalOperations import computeAbsoluteValue, computeAnd, computeOr, computeTimedAlways, computeNot, computeTimedEventually
	from ._signalOperations import computeTimedUntil, computeUntimedUntil, computeUntimedEventually

	from ._signalBuiltIns import __eq__, __repr__, __str__