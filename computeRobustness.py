import pickle
from stl.signals import Signal, SignalList
import antlr4 as a4
import stl.parsing as stlParse
import os

# Configuration
dataFile = "stlTool/openAI/data.pickle"
signalDataFile = "stlTool/openAI/signals.pickle"
formulaFile = "stlTool/openAI/formulas/cartpoleFormula.txt"
robustnessesFile = "stlTool/robustnesses.pickle"

if not os.path.exists(signalDataFile):
	# Load data and create STL tree
	with open(dataFile, 'rb') as f:
		data = pickle.load(f)
	# Convert the data into Signals
	# data contains the log of training episodes.
	# It's a list of lists of tuples. Each tuple is the output of one timestep in an episode, each inner list is an episode.
	# We must have one Signal for cart and one signal for pole position per episode. So 2 different lists of signals
	cartSignals, poleSignals = [], []
	i = 0
	for episode in data:
		# Signal names must match the names used in the formula!
		cartSignal: Signal = Signal(f"c")
		poleSignal: Signal = Signal(f"p")
		time = 0
		for timestep in episode:
			# Time step is [obs, reward, done, note]
			# With obs a 4-tuple: cart pos, cart vel, pole ang, pole angvel
			cartSignal.emplaceCheckpoint(time, timestep[0][0])
			poleSignal.emplaceCheckpoint(time, timestep[0][2])
			time += 1
		cartSignals.append(cartSignal)
		poleSignals.append(poleSignal)
		i += 1

	with open(signalDataFile, 'wb') as f:
		pickle.dump((cartSignals, poleSignals), f, pickle.HIGHEST_PROTOCOL)
else:
	with open(signalDataFile, "rb") as f:
		cartSignals, poleSignals = pickle.load(f)

# Create the STL tree from given formula file
parser = stlParse.stlParser(
    a4.CommonTokenStream(stlParse.stlLexer(a4.FileStream(formulaFile, encoding='utf-8')))
)
tree = parser.content()
listener = stlParse.CustomStlListener()
walker = a4.ParseTreeWalker()
walker.walk(listener, tree)
parser.addParseListener(listener)
stlTree = listener.stlTree

# Output of the tree
with open('stlTree.dot', 'w') as f:
	stlTree.toDot(f)

# Perform the computation

if not os.path.exists(robustnessesFile):
	robustnesses = []
	index = 0
	for cartSignal, poleSignal in zip(cartSignals, poleSignals):
		if any([abs(x) > 2.4 for x in cartSignal.getValues()]):
			breakpoint = True
		r = stlTree.validate(SignalList([cartSignal, poleSignal]))
		robustnesses.append(r)
		if index % 25 == 0:
			print(f"Validated episode {index}")
		index += 1
	print(robustnesses)
	with open(robustnessesFile, "wb") as f:
		pickle.dump(robustnesses, f, pickle.HIGHEST_PROTOCOL)
else:
	with open(robustnessesFile, "rb") as f:
		robustnesses = pickle.load(f)

import matplotlib.pyplot as plt

plt.plot(
    [i for i in range(len(robustnesses))], [min(r.getValues()) for r in robustnesses], color='blue'
)
plt.plot([i for i in range(len(robustnesses))], [0] * len(robustnesses), color='red')
plt.title("Minimum robustness per training episode")
plt.show()

# 	# Validate the signals with the STL formula
# 	result = stlTree.validate(signals2, semantic=argv[3].lower(), plot=True)
# 	print(result)

# 	# import numpy as np
# 	# numpy_array = np.array(result[:2])
# 	# df = pd.DataFrame(numpy_array.T, columns=['s_t', 's'])
# 	# df.to_csv('angles_ep5_bool.csv', index=False)

# 	# End the timer of the whole process
# 	# end = time.time()
# 	# print(f'time for the full operation: {end - start}s')

# if __name__ == '__main__':
# 	#main(sys.argv)
# 	main(['', 'formula.stl', 'signals/ex_1c.csv', 'quantitative'])