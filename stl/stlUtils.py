import numpy
from .signals import Signal, BooleanSignal, SignalList
import math
from typing import Tuple, Union
import warnings
from .utility import Interval


def getPunctualIntersection(s1: Signal, s2: Signal, semantic='quantitative') -> SignalList:
	# TODO: Replace this with an operation on Signal class
	# TODO: Split this into parts (separate quantitative & boolean + more probably)
	# print(f"COMPUTING {semantic} PUNCT INTERSECT; parameters = ")
	# for i in [s1, s2]:
	# 	print(f"\t{i}")
	assert type(s1) == type(s2), "Operation is unsupported between signals of different semantics."
	signalType = type(s1)
	if s1.getCheckpointCount() == 0 or s2.getCheckpointCount() == 0:
		# print(s1)
		# print(s2)
		# print("PunctualIntersect short-circuit to empty signal")

		return [signalType(), signalType()]

	i_1 = 0
	i_2 = 0
	start = max(min(s1.getTimes()), min(s2.getTimes()))  # The start of punctual intersection
	end = min(max(s1.getTimes()), max(s2.getTimes()))  # The end of punctual intersection

	# TODO: Do we care about the amount of time steps or the actual time? 
	# It seems to make more sense that we would care about the actual time, to me.

	# Find how many time steps are passed in each signal to get to start
	# (Only one signal of two has defined values before start)
	while i_1 < len(s1.getTimes()) and s1.getTime(i_1) < start:
		i_1 += 1
	while i_2 < len(s2.getTimes()) and s2.getTime(i_2) < start:
		i_2 += 1

	temp_1, temp_2 = signalType(), signalType()

	# TODO: shouldn't this and the addition at the end be skipped? -> what isn't know, isn't know
	# Add the values at the time steps till start
	# We assume that the signals are constant (derivative = 0) before their first know value
	for i in range(i_1):
		temp_1.addCheckpoint(s1.getCheckpoint(i))
		temp_2.emplaceCheckpoint(s1.getTime(i), s2.getValue(0), 0)
	for i in range(i_2):
		# Add a value at the time step that is defined in s2 and not in s1
		temp_1.emplaceCheckpoint(s2.getTime(i), s1.getValue(0), 0)
		temp_2.addCheckpoint(s2.getCheckpoint(i))

	while i_1 < len(s1.getTimes()) and i_2 < len(s2.getTimes()) and (s1.getTime(i_1) <= end or s2.getTime(i_2) <= end):
		if s1.getTime(i_1) == s2.getTime(i_2):  # Both signals are defined at the time step
			temp_1.addCheckpoint(s1.getCheckpoint(i_1))
			temp_2.addCheckpoint(s2.getCheckpoint(i_2))
			i_1 += 1
			i_2 += 1
		elif s1.getTime(i_1) < s2.getTime(i_2):  # s2 is not defined at the i_1 time step where s1 is defined
			if semantic == 'quantitative':
				# TODO: Why do we have to compute the derivative? Can't we just take it from Signal?
				# Derivative of s2 i_2 - 1 * time difference + value of s2 at i_2 - 1 i.e. interpolate the signal value
				value = (s2.getValue(i_2) - s2.getValue(i_2 - 1)) / (s2.getTime(i_2) - s2.getTime(i_2 - 1)) * (s1.getTime(i_1) - s2.getTime(i_2 - 1)) + s2.getValue(i_2 - 1)
			else:
				value = (s2.getValue(i_2 - 1))
			temp_2.emplaceCheckpoint(s1.getTime(i_1), value, s2.getDerivative(i_2 - 1))
			temp_1.addCheckpoint(s1.getCheckpoint(i_1))
			i_1 += 1
		elif s1.getTime(i_1) > s2.getTime(i_2):  # s1 is not defined at the i_2 time step where s2 is defined
			if semantic == 'quantitative':
				value = (s1.getValue(i_1) - s1.getValue(i_1 - 1)) / (s1.getTime(i_1) - s1.getTime(i_1 - 1)) * (s2.getTime(i_2) - s1.getTime(i_1 - 1)) + s1.getValue(i_1 - 1)
			else:
				value = s1.getValue(i_1 - 1)
			temp_1.emplaceCheckpoint(s2.getTime(i_2), value, s1.getDerivative(i_1 - 1))
			temp_2.addCheckpoint(s2.getCheckpoint(i_2))
			i_2 += 1
		else:
			raise RuntimeError("Something went wrong in getPunctualIntersection")

	# Fill the values from end on
	# We assume that the signals are having a constant derivative from their last known value (should always be 0)
	for i in range(i_1, s1.getCheckpointCount()):
		temp_1.addCheckpoint(s1.getCheckpoint(i))
		# TODO: Verify if this new logic is correct
		# Literal translation commented below; possible correction uncommented.
		#value = temp_2.getValue(-1) + (temp_2.getTime(-1) - temp_2.getTime(-2)) * temp_2.getDerivative(-1)
		value = temp_2.getValue(-1) + (s1.getTime(i) - temp_2.getTime(-1)) * temp_2.getDerivative(-1)
		# This one makes more sense: We create a new point at time s1.getTime(i)
		# So we should compute the difference we expect over the duration from the previous timestamp until the next one
		# The gap temp_2.getTime(-2) -> temp_2.getTime(-1) could be much larger than the gap between s1.getTime(i) and temp_2.getTime(-1)
		# Which would lead to errors in the values

		temp_2.emplaceCheckpoint(s1.getTime(i), value, temp_2.getDerivative(-1))
	for i in range(i_2, s2.getCheckpointCount()):
		temp_2.addCheckpoint(s2.getCheckpoint(i))
		# TODO: Verify logic; see reasoning above.
		#value = temp_1.getValue(-1) + (temp_1.getTime(-1) - temp_1.getTime(-2)) * temp_1.getDerivative(-1)
		value = temp_1.getValue(-1) + (s2.getTime(i) - temp_1.getTime(-1)) * temp_1.getDerivative(-1)
		temp_1.emplaceCheckpoint(s2.getTime(i), value, temp_1.getDerivative(-1))
	# print(f"Punctual Intersection: ")
	# print(f"\t{temp_1}")
	# print(f"\t{temp_2}")
	return SignalList([temp_1, temp_2])


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
	# TODO: Replace this with an operation on Signal class
	# print(f"CALCULATE {operator} (and_or), PARAMETERS:")
	# for i in [x, y]:
	# 	print(f"\t{i}")
	# print(f"PUNCTUAL INTERSECT RESULT: {getPunctualIntersection(x, y)}")
	x, y = getPunctualIntersection(x, y)
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
	return result
