import numpy
from .signals import Signal, BooleanSignal, SignalList
from .utility import line_intersection
import math
from typing import Tuple, Union
import warnings

# Get the value of a signal at time step t
def getAffinePoint(signal: Signal, t: float) -> float:
	# TODO: Replace this with an operation on Signal class
	if t > signal.getLargestTime():
		# Compute using derivative if it falls outside of known values
		return signal.getValue(-1) + signal.getDerivative(-1) * (t - signal.getTime(-1))
	i = 0
	# If it's within known values, find the correct time step
	while signal.getTime(i) < t:
		i += 1
	if i == 0 or signal.getTime(i) == t:
		# If point before signal started, return first data point
		# If it's an exact data point in the signal, return corresponding value
		return signal.getValue(i)
	elif i >= signal.getCheckpointCount():
		# If it's after the end of signal, return last data point
		return signal.getValue(-1)
	else:
		# If it's somewhere between two data points, interpolate
		value = signal.getValue(i - 1)
		value += (signal.getValue(i) - signal.getValue(i-1)) / ((signal.getTime(i) - signal.getTime(i-1)) * t - signal.getTime(i-1))
		return value

# Get a derivative of the signal at time step t
def getAffineDerivative(signal: Signal, t: float):
	# TODO: Replace this with an operation on Signal class
	if t < signal.getTime(0):
		return 0
	for i in range(signal.getCheckpointCount()):
		if t < signal.getTime(i):
			# Signal is linearly interpolated between points, so derivative is constant on the interval [i-1, i)
			return signal.getDerivative(i-1)


# Get an interval of a signal between time steps a and b
# If half open, the last value of time step b will not be included
def getSignalInterval(signal: Signal, a: float, b: float, half_open: bool=False) -> Signal:
	# TODO: Replace this with an operation on Signal class
	constructedSignalName = f"SignalInterval(<{signal.getName()}>, {a}, {b}, {half_open})"
	if a > signal.getTime(-1):
		return Signal(constructedSignalName, [a, b+1], [signal.getValue(-1)]*2, [0, 0])
	elif b < signal.getTime(0):
		return Signal(constructedSignalName, [a, b+1], [signal.getValue(0)]*2, [0, 0])
	
	# Find the first value of the signal that is in the interval
	x = signal.getSmallestTimeAfter(a)

	# If the interval is [a, a]
	if a == b:
		if half_open:
			# In case of half open, that's an empty interval
			warnings.warn("Returning empty signal in getSignalInterval")
			return Signal()
		else:
			# If closed, we should get one value at time a
			warnings.warn("Dropped some derivative code here, verify that the functionality is correct.")

			# if signal[0].index(x) == 0:
			# 	derivative = 0
			# else:
			# 	derivative = signal[2][signal[0].index(x) - 1]
			return Signal(constructedSignalName, [a], [getAffinePoint(signal, a)], [0])
	# Search the last value of the signal that is in the interval
	# Inclusive if the interval is closed
	y = signal.getLargestTimeBefore(b, not half_open)
	# Now, [x, y] is the interval in signal checkpoints, with x >= a and y <= b.
	result = Signal()
	# Do this separately since Signal only allows construction in ascending order of time
	if x > a:
		# We dropped part of the interval here, because we don't have an exact checkpoint. Compute best estimate.
		result.emplaceCheckpoint(a, getAffinePoint(signal, a), numpy.diff([signal.getValue(0), signal.getValue(1)]) / numpy.diff([signal.getTime(0), signal.getTime(1)]))
	else:
		# Handle the case where we had an exact checkpoint
		assert x == a, "x < a should be impossible through program logic."
		result.addCheckpoint(signal.getCheckpoint(signal.getIndexForTime(x)))
	for signalvalue in signal.getSubset(x, y):
		result.addCheckpoint(signalvalue)
	if y < b:
		result.emplaceCheckpoint(b, getAffinePoint(signal, b), numpy.diff([signal.getValue(-2), signal.getValue(-1)] / numpy.diff([signal.getTime(-2), signal.getTime(-1)])))
	else:
		assert y == b, "y > b should be impossible through program logic."
		if not half_open:
			# If it's half open, the limit value should be excluded
			result.addCheckpoint(signal.getCheckpoint(signal.getIndexForTime(b)))
	return result

def getPunctualIntersection(s1: Signal, s2: Signal, semantic='quantitative') -> SignalList:
	# TODO: Replace this with an operation on Signal class
	# TODO: Split this into parts (separate quantitative & boolean + more probably)
	# print(f"COMPUTING {semantic} PUNCT INTERSECT; parameters = ")
	# for i in [s1, s2]:
	# 	print(f"\t{i}")
	if s1.getCheckpointCount() == 0 or s2.getCheckpointCount() == 0:
		# print(s1)
		# print(s2)
		# print("PunctualIntersect short-circuit to empty signal")
		return [Signal(), Signal()]

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

	temp_1, temp_2 = Signal(), Signal()

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
def calculate_and_or(x, y, operator='and'):
	# TODO: Replace this with an operation on Signal class
	# print(f"CALCULATE {operator} (and_or), PARAMETERS:")
	# for i in [x, y]:
	# 	print(f"\t{i}")
	# print(f"PUNCTUAL INTERSECT RESULT: {getPunctualIntersection(x, y)}")
	x, y = getPunctualIntersection(x, y)
	OPERATORS = {'or': lambda x, y: x > y, 'and': lambda x, y: x < y}
	temp = Signal()
	last = None  # Indicating which signal had the last max/min
	for i in range(x.getCheckpointCount()):
		if x.getValue(i) == y.getValue(i):
			last = None
			temp.addCheckpoint(x.getCheckpoint(i))
			temp[0].append(x[0][i])
			temp[1].append(x[1][i])
			temp[2].append(x[2][i])
		elif OPERATORS[operator](x[1][i], y[1][i]):
			if last == 'y':
				inter = line_intersection(
				    [[x[0][i - 1], x[1][i - 1]], [x[0][i], x[1][i]]], [[y[0][i - 1], y[1][i - 1]], [y[0][i], y[1][i]]]
				)
				temp[0].append(inter[0])
				temp[1].append(inter[1])
				temp[2].append(x[2][i - 1])
			last = 'x'
			temp[0].append(x[0][i])
			temp[1].append(x[1][i])
			temp[2].append(x[2][i])
		elif OPERATORS[operator](y[1][i], x[1][i]):
			if last == 'x':
				inter = line_intersection(
				    [[x[0][i - 1], x[1][i - 1]], [x[0][i], x[1][i]]], [[y[0][i - 1], y[1][i - 1]], [y[0][i], y[1][i]]]
				)
				temp[0].append(inter[0])
				temp[1].append(inter[1])
				temp[2].append(y[2][i - 1])
			last = 'y'
			temp[0].append(y[0][i])
			temp[1].append(y[1][i])
			temp[2].append(y[2][i])
	return temp
