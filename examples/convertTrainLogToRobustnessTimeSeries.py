""" Set of functions to convert agent training log for various environments into a simple set of [input -> robustness] data """
# pylint: disable-all
# Adjust path so imports work as expected
import os
import sys

sys.path.insert(0, f"{os.getcwd()}/stlTool")
import stl
from stl.signals import Signal, SignalList
from stl.utility import Interval
import antlr4 as a4
from typing import List, Callable, Tuple
import time

def normalizeCart(value: float) -> float:
	return value / 2.4


def normalizePole(value: float) -> float:
	return value / 0.2095


def normalizeCartpole(index: int, value: float) -> float:
	if index == 0:
		return normalizeCart(value)
	if index == 2:
		return normalizePole(value)
	raise NotImplementedError("Unreachable")


def normalizeMountaincar(index: int, value: float) -> float:
	assert index == 0
	return (value + 0.3) / 0.9

def convertCartpole() -> None:
	""" Handle conversion from training log to robustness time series for the Cartpole environment """
	signals = {0: 'c', 2: 'p'}
	outFile = 'stlTool/examples/cartpole/data_convertedQQ.py'
	if os.path.exists(outFile):
		print(
		    "The output path already exists - assuming computation is unnecessary. Please rename target file if required."
		)
		return None
	# Expensive import, so do it only when required
	from examples.cartpole.data import trainingData as cartpoleTrainingData
	# Use a formula with normalized data, so we have equal impacts from the two signals.
	formula = "(([]{0,50}(0.5-c))^([]{0,50}(0.5+c)))^(([]{0,50}(0.5-p))^([]{0,50}(0.5+p)))"
	minimumLength = 50  # Size of the largest window - no meaningful computation if this isn't reached

	__conversionHelper(formula, signals, minimumLength, cartpoleTrainingData, outFile, normalizeCartpole)


def convertMountaincar() -> None:
	""" Handle conversion from training log to robustness time series for the mountaincar environment """
	outFile = 'stlTool/examples/mountaincar/data_convertedQQ.py'
	if os.path.exists(outFile):
		print(
		    "The output path already exists - assuming computation is unnecessary. Please rename target file if required."
		)
		return None
	from examples.mountaincar.data import trainlog as mountaincarTrainingData
	formula = "<>{0, 50}(p - 0.306)"
	minimumLength = 50
	signals = {0: 'p'}
	__conversionHelper(formula, signals, minimumLength, mountaincarTrainingData, outFile, normalizeMountaincar)


def __conversionHelper(
    stlFormula: str, signals: dict, minLength: int, data: List[Tuple], outputPath: str, normalizeFunction: Callable
) -> None:
	""" Helper function to handle conversion from training log to robustness timeseries
	stlFormula is the (string form) formula we base the robustness computation on
	Signals should be dictionary: {observationIndex: name}.
	Data should be a list of training episodes that we will compute the robustness over, using the given stlFormula.
	Output path is a file to write the result to."""
	parser = stl.parsing.stlParser(a4.CommonTokenStream(stl.parsing.stlLexer(a4.InputStream(stlFormula))))
	tree = parser.content()
	listener = stl.parsing.CustomStlListener()
	walker = a4.ParseTreeWalker()
	walker.walk(listener, tree)
	parser.addParseListener(listener)
	stlTree = listener.stlTree
	with open("mytree.dot", "w") as f:
		stlTree.toDot(f)

	results = []
	for index in range(len(data)):
		currentEpisodeData = data[index]
		currentSignals = SignalList()
		for signalIndex in signals:
			signalName = signals[signalIndex]
			signalValues = []
			for outputTuple in currentEpisodeData:
				observation = outputTuple[0]
				value = normalizeFunction(signalIndex, observation[signalIndex])
				signalValues.append(value)
			signalTimestamps = list(range(len(signalValues)))
			currentSignals.append(Signal(signalName, signalTimestamps, signalValues))
		# If we don't have enough data, don't add it
		if any(c.getDefinedTimeInterval().size() < minLength for c in currentSignals):
			continue
		# In case we want to do performance testing, we don't do the validation here
		# So comment the two lines below, and uncomment the one below that in that case.
		# result = stlTree.validate(currentSignals)
		# results.append((currentSignals, result))
		results.append((currentSignals, Signal("placeholder, dontuse", [0], [0], [0])))
		# End of section that must be (un)commented when (not) doign perf measurement
		if index % 10 == 0:
			print(f"Handled episode index={index} robustness computation!")
	# These lines should be uncommented when running the (offline) performance statistics experiments


	start = time.time()
	for episode in results:
		stlTree.validate(episode[0])
	end = time.time()
	print(f"Computation took {end-start} seconds")

	# Don't do file write; since we don't fill in result adequately.
	return
	# End of section to be commented when not performing perf measurement


	# These lines should be uncommented when running the (online) performance statistics experiments
	# Neural networks compute per time window, so we should mimic that here for things to be comparable
	# perfLogSignals = []
	# results: List[List[List[Signal]]]
	# print("conversion start")
	# for j in range(len(results)):
	# 	if len(signals) == 2: # Dirty hack to check for cartpole
	# 		# If cartpole, compute comparable to ensure same timestamps
	# 		results[j] = (list(Signal.computeCheckpointsForComparableSignal(results[j][0][0], results[j][0][1])), results[j][1])
	# 	for i in range(results[j][0][0].getCheckpointCount()):
	# 		item = SignalList([results[j][0][0].computeInterval(Interval(results[j][0][0].getTime(i), results[j][0][0].getTime(i) + minLength)).shift(-1*results[j][0][0].getTime(i))])
	# 		if item[0].getDefinedTimeInterval().size() < minLength:
	# 			break
	# 		if len(signals) == 2:
	# 			item.append(results[j][0][1].computeInterval(Interval(results[j][0][1].getTime(i), results[j][0][1].getTime(i) + minLength)).shift(-1*results[j][0][1].getTime(i)))

	# 		perfLogSignals.append(item)

	# print("conversion ended")
	# start = time.time()
	# for i in range(len(perfLogSignals)):
	# 	stlTree.validate(perfLogSignals[i])
	# 	if i % 2500 == 0:
	# 		print(f"Handled index {i} out of {len(perfLogSignals)-1}")
	# end = time.time()
	# print(f"Computation took {end - start} seconds")
	# # We don't write the correct values to the list, so don't write to file.
	# return
	# End of section to be commented when not performing perf measurement

	with open(outputPath, 'w') as f:
		f.write("import os\nimport sys\nsys.path.insert(0, f'{os.getcwd()}/stlTool')\nfrom stl.signals import Signal\n")
		f.write("data = [\n\t")
		f.write(',\n\t'.join(x.__str__() for x in results))
		f.write("\n]")



# One of these calls can be commented if the data for only one of the environments is required.
convertCartpole()
# convertMountaincar()