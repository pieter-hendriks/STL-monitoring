""" Set of functions to convert agent training log for various environments into a simple set of [input -> robustness] data """
# pylint: disable-all
# Adjust path to imports work as expected
import os
import sys

sys.path.insert(0, f"{os.getcwd()}/stlTool")
import stl
import antlr4 as a4
import numpy as np

# TODO: Change path back to data_converted.py rather than data_converted_FAKE.py
# Change made to allow some debugging
def convertCartpole():
	""" Handle conversion from training log to robustness time series for the Cartpole environment """
	signals = {0: 'c', 2: 'p'}
	outFile = 'stlTool/examples/cartpole/data_converted_FAKE.py'
	if os.path.exists(outFile):
		print(
		    "The output path already exists - assuming computation is unnecessary. Please rename target file if required."
		)
		return None
	# Expensive import, so do it only when required
	from examples.cartpole.data import trainingData as cartpoleTrainingData
	formula = "(([]{0,50}(2.4-c))^([]{0,50}(2.4+c)))^(([]{0,50}(0.209-p))^([]{0,50}(0.209+p)))"
	minimumLength = 50  # Size of the largest window - no meaningful computation if this isn't reached
	__conversionHelper(formula, signals, minimumLength, cartpoleTrainingData, outFile)


def convertMountaincar():
	""" Handle conversion from training log to robustness time series for the mountaincar environment """
	outFile = 'stlTool/examples/mountaincar/data_converted.py'
	if os.path.exists(outFile):
		print(
		    "The output path already exists - assuming computation is unnecessary. Please rename target file if required."
		)
		return None
	from examples.mountaincar.data import trainlog as mountaincarTrainingData
	formula = "<>{0, 50}(p - 0.45)"
	minimumLength = 50
	signals = {0: 'p'}
	__conversionHelper(formula, signals, minimumLength, mountaincarTrainingData, outFile)


def __conversionHelper(stlFormula, signals, minLength, data, outputPath):
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

	results = []
	for index in range(len(data)):
		currentEpisodeData = data[index]
		if len(currentEpisodeData) < minLength:
			# Drop all episodes we can't meaningfully compute robustness for.
			# The result will always be an empty signal from the algorithm - not useful for training the estimator
			continue
		currentSignals = stl.signals.SignalList()
		for signalIndex in signals:
			signalName = signals[signalIndex]
			signalValues = []
			for outputTuple in currentEpisodeData:
				observation = outputTuple[0]
				signalValues.append(observation[signalIndex])
			signalTimestamps = list(range(len(signalValues)))
			currentSignals.append(stl.signals.Signal(signalName, signalTimestamps, signalValues))
		result = stlTree.validate(currentSignals)
		results.append((currentSignals, result))
		print(currentSignals[0])
		print(currentSignals[1])
		print(result)

		with open("mytree.dot", "w") as f:
			stlTree.toDot(f)

		exit(1)

		if index % 10 == 0:
			print(f"Handled index={index} robustness computation!")

	# with open(outputPath, 'w') as f:
	# 	f.write("import os\nimport sys\nsys.path.insert(0, f'{os.getcwd()}/stlTool')\nfrom stl.signals import Signal\n")
	# 	f.write("data = [\n\t")
	# 	f.write(',\n\t'.join(x.__str__() for x in results))
	# 	f.write("\n]")


convertCartpole()