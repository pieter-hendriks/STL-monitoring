import os
import pickle
from turtle import pos
from stl.signals import Signal, SignalList
from stl.tree import UntilNode
import antlr4 as a4
import stl.parsing as stlParse
import cProfile

# Configuration
prefix = "stlTool/openAI/mountaincar"
dataPickle = f"{prefix}/data.pickle"
signalDataFile = f"{prefix}/signals.pickle"
formulaFile = f"{prefix}/formula.txt"
robustnessesFile = f"{prefix}/robustnesses.pickle"

if not os.path.exists(signalDataFile):
	if not os.path.exists(dataPickle):
		from openAI.mountaincar.data import trainlog
		with open(dataPickle, 'wb') as f:
			pickle.dump(trainlog, f, protocol=pickle.HIGHEST_PROTOCOL)
	else:
		with open(dataPickle, 'rb') as f:
			trainlog = pickle.load(f)
	# trainlog is list of lists
	# List of episodes, each episode is a list of observations. Observation: (next_state, reward, done, note)

	# Observations need to be turned into Signals; x-axis position, velocity (p and v)
	episodes = []
	for episode in trainlog:
		positionSignal: Signal = Signal("p", range(len(episode)), [x[0][0] for x in episode])
		velocitySignal: Signal = Signal("v", range(len(episode)), [x[0][1] for x in episode])
		episodes.append((positionSignal, velocitySignal))

	with open(signalDataFile, 'wb') as f:
		pickle.dump(episodes, f, protocol=pickle.HIGHEST_PROTOCOL)
else:
	with open(signalDataFile, 'rb') as f:
		episodes = pickle.load(f)

# Create the STL tree from given formula file
parser = stlParse.stlParser(a4.CommonTokenStream(stlParse.stlLexer(a4.FileStream(formulaFile, encoding='utf-8'))))
tree = parser.content()
listener = stlParse.CustomStlListener()
walker = a4.ParseTreeWalker()
walker.walk(listener, tree)
parser.addParseListener(listener)
stlTree = listener.stlTree

# Output of the tree
with open('stlTree.dot', 'w') as f:
	stlTree.toDot(f)

untilNode: UntilNode = stlTree.children[0]


# Perform the computation
def computeRobustness():
	if not os.path.exists(robustnessesFile):
		robustnesses = []
		index = 0
		for positionSignal, velocitySignal in episodes[0:1]:
			r = stlTree.validate(SignalList([positionSignal, velocitySignal]))
			robustnesses.append(r)
			if index % 25 == 0:
				print(f"Validated episode {index}")
			index += 1
		print(robustnesses)
		# with open(robustnessesFile, "wb") as f:
		# 	pickle.dump(robustnesses, f, pickle.HIGHEST_PROTOCOL)
	else:
		with open(robustnessesFile, "rb") as f:
			robustnesses = pickle.load(f)
	return robustnesses


untilNode.useEfficientAlgorithm()
efficientRobustnesses = computeRobustness()
untilNode.useSyntaxAlgorithm()
syntaxRobustnesses = computeRobustness()

assert efficientRobustnesses[0].lenientEquals(syntaxRobustnesses[0]), "Newfn test"
assert efficientRobustnesses[0] == syntaxRobustnesses[0], "nonewfn"
assert efficientRobustnesses == syntaxRobustnesses, "Assertion failed; mismatch"