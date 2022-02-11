from .formulanode import FormulaNode
from ..valuenodes import ValueNode
from ....stlUtils import calculate_and_or, getPunctualIntersection, getBooleanIntersection
from ....utility import Interval
from ....signals import Signal, BooleanSignal, SignalList, SignalValue
from typing import Tuple, List
from numbers import Number
import warnings

class UntilNode(FormulaNode):
	def __init__(self) -> None:
		super().__init__()
		self.__useShortAlgorithm = True
	
	def useShortAlgorithm(self):
		self.__useShortAlgorithm = True

	def useLongAlgorithm(self):
		self.__useShortAlgorithm = False

	def shortAlgorithm(self, size: int, childResults: List[Signal], interval: Interval) -> Signal:
		output: Signal = Signal("until")
		print("Until input:")
		print(f"\ta={interval.getLower()}")
		print(f"\tb={interval.getUpper()}")
		print(f"\tleftChild={childResults[0].oldFormat()}")
		print(f"\trightChild={childResults[1].oldFormat()}")
		print(size)
		for i in range(size):
			print('loop0')
			t = childResults[1].getTime(i)
			print(f"t={t}")
			print(f"a={interval.getLower()}")
			print(f"b={interval.getUpper()}")
			print(f"timeinterval={interval + t}")
			inter_2 = childResults[1].getInterval(interval + t, half_open=False)
			print(f"int2: {inter_2.oldFormat()}")
			values = []
			derivatives = []
			for j in range(inter_2.getCheckpointCount()):
				print('loop1')
				k = inter_2.getTime(j)
				inter_1 = childResults[0].getInterval(Interval(t, k), half_open=False)
				print(f"int1: {inter_1.oldFormat()}")
				values.append(min(inter_2.getValue(j), min(inter_1.getValues())))
				derivatives.append(min(inter_2.getDerivative(j), min(inter_1.getDerivatives())))
			print("endloop1")
			output.emplaceCheckpoint(t, max(values), max(derivatives))
		print(f"endloop0: {output.oldFormat()}")
		# if output.oldFormat() != [[0, 1, 2, 3, 4], [1, 1, 1, 1, -1], [0, 0, -2, -1, 0.0]]:
		# 	exit(1)
		for i in reversed(range(output.getCheckpointCount())):
			print("loop2")
			updatedLastTime = childResults[0].getTime(-1) - interval.getUpper()
			if output.getTime(i) > updatedLastTime:
				print('if1')
				sv = output.popCheckpoint()
				if sv.getTime() < updatedLastTime:
					print('if2')
					output.emplaceCheckpoint(updatedLastTime, output.getAffinePoint(updatedLastTime), output.getDerivative(-2))
		print('endloop2')
		#print(f"Until result=\n\t[{output.getTimes()}, {output.getValues()}, {output.getDerivatives()}]")
		# warnings.warn("We haven't implemented correct derivatives computation in the short algorithm. Source implementation also doesn't really handle that case at all.")
		# raise NotImplementedError("ShortAlgorithm derivative handling is incomplete (also I don't know if that matters at all")
		output.recomputeDerivatives()
		return output

	# TODO: Any reason we can't just merge computeAnd/computeOr?
	# Or remove them entirely? calculate_and_or does the getPunctualIntersection as first line.
	# Do we need to run that twice?
	def __computeAnd(self, x, y):
		#x, y = getPunctualIntersection(x, y)
		return calculate_and_or(x, y, 'and')

	def __computeOr(self, x, y):
		#x, y = getPunctualIntersection(x, y)
		return calculate_and_or(x, y, 'or')


	# TODO: This should be an operation on Signal.
	def __shift(self, y, v):
		# y - v
		# Drop all where y - v < 0
		# Return remaining data points
		# print(f"Shift called: ({y}, {v})")
		# Shift the timestamps
		shiftedTimestamps = [t - v for t in y[0] if t - v >= 0]
		# If all time steps (after shift) are negative,
		if len(shiftedTimestamps) == 0:
			# Return empty signal
			return [[], [], []]
		# Construct the shifted signal; match shifted timestamps with their corresponding value/derivative
		shiftedSignal = [shiftedTimestamps, y[1][-len(shiftedTimestamps):], y[2][-len(shiftedTimestamps):]]
		# If no values were deleted, return the signal
		if len(shiftedTimestamps) == len(y[0]):
			return shiftedSignal
		# Add a point at time step 0 if the derivative of the last deleted point isn't 0
		# TODO: Does derivative being zero 0 in last point matter? If it is, we just add value with same v and dv==0
		if shiftedSignal[0][0] != 0 and y[2][-(len(shiftedTimestamps) + 1)] != 0:
			# Prepend a timestamp zero
			shiftedSignal[0].insert(0, 0)
			# Prepend the signal value
			shiftedSignal[1].insert(0, getAffinePoint(y, v))
			# Compute the derivative; change in v over [t_0, t_1]
			deltaValue = shiftedSignal[1][1] - shiftedSignal[1][0]
			deltaTime = shiftedSignal[0][1] - shiftedSignal[0][0]
			shiftedSignal[2].insert(0, deltaValue / deltaTime)
		# print(f"Shift return: {shiftedSignal}")
		return shiftedSignal

	def __computeEventually(self, x, a, b, t_0=None):
		# print("COMPUTE EVENTUALLY CALLED, PARAMETERS:")
		# for i in [x, a, b, t_0]:
			# print(f"\t{i}")
		if t_0 is None:
			t_0 = x[0][0]
		# print(f"x: {x}\na: {a}\nb: {b}")
		y_a = self.__shift(x, a)
		# print(y_a)
		y_b = self.__shift(x, b)
		# print(y_b)
		y = calculate_and_or(y_a, y_b, 'or')
		# Initialize variables
		s = x[0][0] - b
		t = s
		i = 0
		M = {x[0][0]}
		z = [[], [], []]

		while t + a < x[0][-1]:
			if i + 1 < len(x[0]) and len(M) > 0:
				t = min(min(M) - a, x[0][i + 1] - b)
			elif len(M) == 0:
				t = x[0][i + 1] - b
			else:
				t = min(M) - a

			if len(M) > 0 and t == min(M) - a:
				M.remove(min(M))
				# not sure if the z computation shouldn't be here... (gives the same result on the examples)
				s = t

			if s >= t_0:
				if len(M) == 0:
					computed_or = y
				else:
					yt_minM = getAffinePoint(x, min(M))
					y_s_t = getSignalInterval(y, Interval(s, t))
					y_constant = [y[0], [yt_minM] * len(y[0]), [0] * len(y[0])]
					computed_or = calculate_and_or(y_s_t, y_constant, 'or')
				print(computed_or)
				print("COMPUTED_OR=^")
				i_s = computed_or[0].index(s)
				i_t = computed_or[0].index(t)

				for index in range(i_s, i_t + 1):
					if computed_or[0][index] not in z[0]:
						z[0].append(computed_or[0][index])
						z[1].append(computed_or[1][index])
						z[2].append(computed_or[2][index])
					else:
						i_z = z[0].index(computed_or[0][index])
						z[1][i_z] = computed_or[1][index]
						z[2][i_z] = computed_or[2][index]

			if i + 1 < len(x[0]) and t == x[0][i + 1] - b:
				while len(M) != 0 and getAffinePoint(x, x[0][i + 1]) >= getAffinePoint(x, max(M)):
					M.remove(max(M))
				M.add(x[0][i + 1])
				i += 1
		return z

	def longAlgorithm(self, size: int, childResults: SignalList, interval: Interval) -> Signal:
		lowerBound = interval.getLower()
		upperBound = interval.getUpper()
		# Begin algorithm for until
		output = Signal("until")
		z_0 = [childResults[1][0], [0] * size, [0] * size]
		i = len(childResults[0][0]) - 2  # Has to be 2, not 1 because we use an  extra +1 in the intervals
		# Because the algorithm doesn't include the last value, we act as if we don't have a half open interval in python
		while i >= 0:
			if childResults[0][2][i] <= 0:
				z_1_new = calculate_and_or([x[i:(i+1) + 1] for x in childResults[1]], [x[i:(i+1) + 1] for x in childResults[0]], 'and')
				z_1 = self.__computeAnd([x[i:(i+1) + 1] for x in childResults[1]], [x[i:(i+1) + 1] for x in childResults[0]])
				z_2 = self.__computeEventually(z_1, lowerBound, upperBound, childResults[0][0][0])
				z_3 = self.__computeAnd([x[i:(i+1) + 1] for x in childResults[0]], z_0)
				z_3_new = calculate_and_or([x[i:(i+1) + 1] for x in childResults[0]], z_0, 'and')
				# print("Comparing computeAnd:")
				# print(f"\t[OLD={z_1}] vs [NEW={z_1_new}]")
				# print(f"\t[OLD={z_3}] vs [NEW={z_3_new}]")
				temp = self.__computeOr(z_2, z_3)
				temp_new = calculate_and_or(z_2, z_3, 'or')
				# print("Comparing computeOr:")
				# print(f"\t[OLD={temp}] vs [NEW={temp_new}]")
			else:
				z_1 = self.__computeEventually([x[i:(i+1) + 1] for x in childResults[1]], lowerBound, upperBound, childResults[0][0][0])
				z_2 = self.__computeAnd(z_1, [x[i:(i+1) + 1] for x in childResults[0]])
				z_2_new = calculate_and_or(z_1, [x[i:(i+1) + 1] for x in childResults[0]], 'and')
				z_3 = self.__computeAnd([childResults[0][0], [childResults[0][0][i + 1]] * size, [0] * size], z_0)
				z_3_new = calculate_and_or([childResults[0][0], [childResults[0][0][i + 1]] * size, [0] * size], z_0, 'and')
				# print("Comparing computeAnd:")
				# print(f"\t[OLD={z_2}] vs [NEW={z_2_new}]")
				# print(f"\t[OLD={z_3}] vs [NEW={z_3_new}]")
				temp = self.__computeOr(z_2, z_3)
				# print("Comparing computeOr:")
				# print(f"\t[OLD={temp}] vs [NEW={temp_new}]")

			t_i = temp[0].index(childResults[1][0][i])
			if childResults[1][0][i + 1] == childResults[1][0][-1]:  # The last (so first in algorithm) pair
				t_i_1 = len(temp[0])
			else:
				t_i_1 = temp[0].index(childResults[1][0][i + 1])
			until[0] = temp[0][t_i:t_i_1] + until[0]
			until[1] = temp[1][t_i:t_i_1] + until[1]
			until[2] = temp[2][t_i:t_i_1] + until[2]
			i -= 1
			# z_0 = [result[0][0], [until[1][until[0].index(result[0][0][i+1])]] * size, [0] * size]  # Should be the last added value?
			z_0 = [childResults[0][0], [until[1][0]] * size, [0] * size]  # Should be the last added value?
		return until

	def quantitativeValidate(self, signals: SignalList, plot: bool=False) -> Signal:
		# Check if one or two formula nodes as children, if one -> add true signal
		if len(self.children) == 4:
			childResults: SignalList = SignalList([self.children[0].quantitativeValidate(signals, plot), self.children[3].quantitativeValidate(signals, plot)])
			childResults = getPunctualIntersection(childResults[0], childResults[1], 'quantitative')
		else:
			# Eventually: EVENTUALLY[a, b] <SIGNAL>: a = children[0]/[-3], b = [1]/[-2], signal = [2]/[-1]
			# This is the 'eventually' operation == '<TRUE> Until[a,b] <signal>'
			assert len(self.children) == 3
			childResult: Signal = self.children[2].quantitativeValidate(signals, plot)
			dummySignal: Signal = Signal("DummyTrueSignal", childResult.getTimes(), [1] * childResult.getCheckpointCount(), [0] * childResult.getCheckpointCount())
			childResults: SignalList = SignalList([dummySignal, childResult])

		size = childResults[0].getCheckpointCount()
		# Get the interval limit values for the interval [a, b]
		aSignal: Signal = self.children[-3].quantitativeValidate(signals, plot)
		bSignal: Signal = self.children[-2].quantitativeValidate(signals, plot)
		assert aSignal.getCheckpointCount() == bSignal.getCheckpointCount() == 1, f"Ambiguous interval sizes. These should be from ValueNodes, which return a single-value Signal."
		interval = Interval(aSignal.getValue(0), bSignal.getValue(0))
		if self.__useShortAlgorithm:
			until = self.shortAlgorithm(size, childResults, interval)
		else:
			until = self.longAlgorithm(size, childResults, interval)
		if plot:
			self.quantitativePlot(until)
		return until

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		# Operator can be unary or binary;
		# Children are 2 integers from the time interval, plus one or two formulas.
		if len(self.children) == 4:
			childResults: SignalList = SignalList([self.children[0].booleanValidate(signals, plot), self.children[3].booleanValidate(signals, plot)])
			childResults = getPunctualIntersection(childResults[0], childResults[1], 'boolean')
		else:
			assert len(self.children) == 3
			childResult: BooleanSignal = self.children[2].booleanValidate(signals, plot)
			dummySignal: BooleanSignal = BooleanSignal("DummyTrueSignal", childResult.getTimes(), [1] * childResult.getCheckpointCount(), [0] * childResult.getCheckpointCount())
			childResults: SignalList = SignalList([dummySignal, childResult])
		size = childResults[0].getCheckpointCount()
		
		aSignal: BooleanSignal = self.children[-3].booleanValidate(signals, plot)
		bSignal: BooleanSignal = self.children[-2].booleanValidate(signals, plot)
		assert aSignal.getCheckpointCount() == bSignal.getCheckpointCount() == 1, f"Ambiguous interval sizes. These should be from ValueNodes, which return a single-value Signal."
		interval = Interval(aSignal.getValue(0), bSignal.getValue(0))
		until = self.booleanValidationImplementation(size, childResults, interval)
		if plot:
			self.plot(until)
		return until

	def booleanValidationImplementation(self, size: int, childResults: SignalList, interval: Interval):
		a = interval.getLower()
		b = interval.getUpper()
		# Get the true intervals of the signals
		intervals_1, intervals_2 = [], []
		temp_1, temp_2 = [], []
		true_1, true_2 = False, False
		for i in range(size):
			if childResults[0].getValue(i) and not true_1:
				true_1 = True
				temp_1.append(childResults[0].getTime(i))
			elif not childResults[0].getValue(i) and true_1:
				true_1 = False
				# temp_1.append(result[0][0][i - 1])  # Closed interval (discrete time steps)
				temp_1.append(childResults[0].getTime(i))  # Half open interval [a,b) (continuous time steps)
				intervals_1.append(temp_1)
				temp_1 = []

			if childResults[1].getValue(i) and not true_2:
				true_2 = True
				temp_2.append(childResults[1].getTime(i))
			elif not childResults[1].getValue(i) and true_2:
				true_2 = False
				# temp_2.append(result[1][0][i - 1])  # Closed interval (discrete time steps)
				temp_2.append(childResults[1].getTime(i))  # Half open interval [a,b) (continuous time steps)
				intervals_2.append(temp_2)
				temp_2 = []
		if true_1:
			temp_1.append(childResults[0].getTime(size - 1))
			intervals_1.append(temp_1)
		if true_2:
			temp_2.append(childResults[1].getTime(size - 1))
			intervals_2.append(temp_2)

		# Decompose and calculate the Until for the decompositions
		intervals_until = []
		for inter_1 in intervals_1:
			for inter_2 in intervals_2:
				intersection = getBooleanIntersection(inter_1, inter_2)
				if intersection:
					interval = [max(0, intersection[0] - b), min(size, intersection[1] - a)]
					if interval[0] > interval[1]:  # Interval doesn't exist
						continue
					intersection = getBooleanIntersection(interval, inter_1)
					if intersection:
						intervals_until.append(intersection)
		# Calculate the entire until, make the intervals true in the until
		until = BooleanSignal("until", childResults[1].getTimes(), [0] * size)
		for interval in intervals_until:
			for timestamp in interval:
				if timestamp in until.getTimes():
					timestampIndex = until.getTimes().index(timestamp)
					until.getCheckpoint(timestampIndex).setValue(1)
				else:
					until.emplaceCheckpoint(timestamp, 1)
			intervalStartIndex = until.getTimes().index(interval[0])
			intervalEndIndex = until.getTimes().index(interval[1])
			for i in range(intervalStartIndex, intervalEndIndex):
				# Iteration (by index) over all time stamps in until part of the interval
				# Half-open interval, so exclude the last value.
				until.getCheckpoint(i).setValue(1)
			until.getCheckpoint(intervalEndIndex).setValue(0)
		for i in reversed(range(until.getCheckpointCount())):
			if until.getTime(i) > childResults[0].getTime(-1) - b:
				if until.getTime(i - 1) < childResults[0].getTime(-1) - b:
					# TODO: Figure out if this code is working properly. Changing the time like that seems fucky.
					# SignalValue is edited to allow it specifically because of this (as of 13/01 - may see other dependencies later)
					# No extra sorting happens in the SortedList after this change - which may cause problems.
					# The asserts wrapping this code ensure no unexpected consequences propagate 
					assert until.getTimes() == sorted(until.getTimes()), "Time was unsorted prior to time modification."
					poppedPoint: SignalValue = until.popCheckpoint()
					until.emplaceCheckpoint(childResults[0].getTime(-1) - b, poppedPoint.getValue(), poppedPoint.getDerivative())
					assert until.getTimes() == sorted(until.getTimes()), "Time modification created an issue."
				else:
					until.popCheckpoint()
		return until

	# def validate(self, signals, semantic='quantitative', plot=False):

	# 	# Check if one or two formula nodes as children, if one -> add true signal
	# 	result = [self.children[-1].validate(signals, semantic, plot)]
	# 	# With two formulas it would be 4 (2 formula, 2 int for interval)
	# 	if len(self.children) == 3:
	# 		result = [[result[0][0], ([1] * len(result[0][0])), ([0] * len(result[0][0]))]] + result
	# 	else:
	# 		result = [self.children[0].validate(signals, semantic, plot)] + result
	# 		result = list(getPunctualIntersection(result[0], result[1], semantic))
	# 	# Get the size for which all needed data is present
	# 	size = len(result[0][0])
	# 	# Get the values
	# 	a = self.children[len(self.children) - 3].validate(signals, semantic, plot)
	# 	b = self.children[len(self.children) - 2].validate(signals, semantic, plot)
	# 	until = []
	# 	if semantic == 'boolean':
	# 		until = self.__booleanValidation(size, result, b, a, [])
	# 	elif semantic == 'quantitative':
	# 		short_algo = True
	# 		until += [[], [], []]
	# 		if short_algo:
	# 			until = self.__shortAlgorithm(size, result, a, b, [[], [], []])
	# 		else:
	# 			until = self.__longAlgorithm(size, result, a, b, [[], [], []])

	# 			def shift(y, v):
	# 				# Shift the signal
	# 				temp = [t - v for t in y[0]]
	# 				i = 0
	# 				# Count how many values have a time step smaller than 0
	# 				while i < len(y[0]) and temp[i] < 0:
	# 					i += 1

	# 				if len(y[0]) == i:
	# 					return [[], [], []]

	# 				result = [temp[i:], y[1][i:], y[2][i:]]
	# 				# Add a point at time step 0 if the derivative of the last deleted point isn't 0
	# 				if i > 0 and result[0][0] != 0 and y[2][i] != 0:
	# 					result[0] = [0] + result[0]
	# 					result[1] = [getAffinePoint(y, v)] + result[1]
	# 					# TODO: Figure out what these diffs are doing?
	# 					# Line was originally super long, so simplified by adding diff1/2 vars
	# 					diff1 = numpy.diff([result[1][0], result[1][1]])
	# 					diff2 = numpy.diff([result[0][0], result[0][1]])
	# 					result[2] = list(diff1 / diff2) + result[2]
	# 				return result

	# 			# TODO: Any reason we can't just merge computeAnd/computeOr?
	# 			def computeAnd(x, y):
	# 				x, y = getPunctualIntersection(x, y)
	# 				return calculate_and_or(x, y)

	# 			def computeOr(x, y):
	# 				x, y = getPunctualIntersection(x, y)
	# 				return calculate_and_or(x, y, 'or')

	# 			def computeEventually(x, t_0=float('inf')):
	# 				if t_0 == float('inf'):
	# 					t_0 = x[0][0]
	# 				y_a = shift(x, a)
	# 				y_b = shift(x, b)
	# 				y = computeOr(y_a, y_b)
	# 				# Initialize variables
	# 				s = x[0][0] - b
	# 				t = s
	# 				i = 0
	# 				M = {x[0][0]}

	# 				z = [[], [], []]

	# 				while t + a < x[0][-1]:
	# 					if i + 1 < len(x[0]) and len(M) > 0:
	# 						t = min(min(M) - a, x[0][i + 1] - b)
	# 					elif len(M) == 0:
	# 						t = x[0][i + 1] - b
	# 					else:
	# 						t = min(M) - a

	# 					if len(M) > 0 and t == min(M) - a:
	# 						M.remove(min(M))
	# 						# not sure if the z computation shouldn't be here... (gives the same result on the examples)
	# 						s = t

	# 					if s >= t_0:
	# 						if len(M) == 0:
	# 							computed_or = y
	# 						else:
	# 							yt_minM = getAffinePoint(x, min(M))

	# 							y_s_t = getSignalInterval(y, s, t)
	# 							y_constant = [y[0], [yt_minM] * len(y[0]), [0] * len(y[0])]
	# 							computed_or = computeOr(y_s_t, y_constant)

	# 						i_s = computed_or[0].index(s)
	# 						i_t = computed_or[0].index(t)

	# 						for index in range(i_s, i_t + 1):
	# 							if computed_or[0][index] not in z[0]:
	# 								z[0].append(computed_or[0][index])
	# 								z[1].append(computed_or[1][index])
	# 								z[2].append(computed_or[2][index])
	# 							else:
	# 								i_z = z[0].index(computed_or[0][index])
	# 								z[1][i_z] = computed_or[1][index]
	# 								z[2][i_z] = computed_or[2][index]

	# 					if i + 1 < len(x[0]) and t == x[0][i + 1] - b:
	# 						while len(M) != 0 and getAffinePoint(x, x[0][i + 1]) >= getAffinePoint(x, max(M)):
	# 							M.remove(max(M))
	# 						M.add(x[0][i + 1])
	# 						i += 1

	# 				return z

	# 			# Begin algorithm for until
	# 			until = [[], [], []]
	# 			z_0 = [result[1][0], [0] * size, [0] * size]
	# 			i = len(result[0][0]) - 2  # Has to be 2, not 1 because we use an  extra +1 in the intervals
	# 			# Because the algorithm doesn't include the last value, we act as if we don't have a half open interval in python
	# 			while i >= 0:
	# 				if result[0][2][i] <= 0:
	# 					z_1 = computeAnd([x[i:(i+1) + 1] for x in result[1]], [x[i:(i+1) + 1] for x in result[0]])
	# 					z_2 = computeEventually(z_1, result[0][0][0])
	# 					z_3 = computeAnd([x[i:(i+1) + 1] for x in result[0]], z_0)
	# 					temp = computeOr(z_2, z_3)
	# 				else:
	# 					z_1 = computeEventually([x[i:(i+1) + 1] for x in result[1]], result[0][0][0])
	# 					z_2 = computeAnd(z_1, [x[i:(i+1) + 1] for x in result[0]])
	# 					z_3 = computeAnd([result[0][0], [result[0][0][i + 1]] * size, [0] * size], z_0)
	# 					temp = computeOr(z_2, z_3)

	# 				t_i = temp[0].index(result[1][0][i])
	# 				if result[1][0][i + 1] == result[1][0][-1]:  # The last (so first in algorithm) pair
	# 					t_i_1 = len(temp[0])
	# 				else:
	# 					t_i_1 = temp[0].index(result[1][0][i + 1])

	# 				until[0] = temp[0][t_i:t_i_1] + until[0]
	# 				until[1] = temp[1][t_i:t_i_1] + until[1]
	# 				until[2] = temp[2][t_i:t_i_1] + until[2]
	# 				i -= 1
	# 				# z_0 = [result[0][0], [until[1][until[0].index(result[0][0][i+1])]] * size, [0] * size]  # Should be the last added value?
	# 				z_0 = [result[0][0], [until[1][0]] * size, [0] * size]  # Should be the last added value?
	# 	if plot:
	# 		self.plot(until)

	# 	# End the timer of the the until process
	# 	# end_1 = time.time()
	# 	# print(f'time for until operation: {end_1 - start_1}s')

	# 	return until