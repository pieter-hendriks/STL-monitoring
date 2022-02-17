import numpy
from .signals import Signal, BooleanSignal, SignalList
import math
from typing import Tuple, Union
import warnings
from .utility import Interval





def getBooleanIntersection(a: Signal, b: Signal) -> Union[bool, Signal]:
	# TODO: Replace this with an operation on Signal class
	warnings.warn("Boolean intersection doesn't use Signal class because idfk what's going on")
	warnings.warn("Fix the type annotation for getBooleanIntersection. a and b are intervals of times; not signals.\n\t\tFind references > figure it out from there.")

	print(f"a = {a}")
	print(f"b = {b}")
	intersection = [max(a[0], b[0]), min([a[-1], b[-1]])]
	if intersection[0] > intersection[1]:
		return False
	else:
		return intersection


# x and y are signals in the form of [t, x, dx]
# operator is one of the following: 'and' or 'or'
def calculate_and_or(x: Signal, y: Signal, operator='and') -> Signal:
	if operator == 'and':
		operation = lambda x, y: x < y
	elif operator == 'or':
		operation = lambda x, y: x > y
	else:
		raise NotImplementedError(f"calculate_and_or not implemented for operation '{operator}'")
	x, y = Signal.computeComparableSignals(x, y)
	result = Signal(operator)
	last = None  # Indicating which signal had the last max/min
	for i in range(x.getCheckpointCount()):
		if x.getValue(i) == y.getValue(i):
			last = None
			result.addCheckpoint(x.getCheckpoint(i))
		elif operation(x.getValue(i), y.getValue(i)):
			if last == 'y':
				intersectionTime, intersectionValue = x.intersectAtIndex(y, i)
				# We compute by continuing at current derivative, so the derivative remains equal to the previous entry
				result.emplaceCheckpoint(intersectionTime, intersectionValue, x.getDerivative(i-1))
			last = 'x'
			result.addCheckpoint(x.getCheckpoint(i))
		else:
		#elif operation(y.getValue(i), x.getValue(i)):
			if last == 'x':
				intersectionTime, intersectionValue = y.intersectAtIndex(x, i)
				# We compute by continuing at current derivative, so the derivative remains equal to the previous entry
				result.emplaceCheckpoint(intersectionTime, intersectionValue, y.getDerivative(i-1))
			last = 'y'
			result.addCheckpoint(y.getCheckpoint(i))
	result.recomputeDerivatives()
	return result
