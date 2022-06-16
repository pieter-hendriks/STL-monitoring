import sys
import pandas as pd
# pylint: disable=unused-wildcard-import
from antlr4 import *
from stl.parsing import stlLexer, CustomStlListener, stlParser
from stl.signals import SignalList
import time
from stl.utility import PlotHelper

def main(formulafile: str, signalfile: str, semantics: str, algorithm: str):
	# Check the STL fomula
	text = FileStream(formulafile, encoding='utf-8')
	lexer = stlLexer(text)
	stream = CommonTokenStream(lexer)
	parser = stlParser(stream)
	tree = parser.content()

	# Make an STL tree
	listener = CustomStlListener()
	walker = ParseTreeWalker()
	walker.walk(listener, tree)
	parser.addParseListener(listener)
	stlTree = listener.stlTree
	if algorithm == 'efficient':
		stlTree.useEfficientAlgorithm()
	elif algorithm == 'syntax':
		stlTree.useSyntaxAlgorithm()
	else:
		raise RuntimeError("Unknown algorithm type")

	# Print the STL tree
	with open('stlTree.dot', 'w') as file:
		stlTree.toDot(file)

	# Read the signals
	signals2 = SignalList.fromCSV(signalfile)

	# Validate the signals with the STL formula
	# s = time.time()
	result = stlTree.validate(signals2, semantic=semantics, plot=True)
	# print(f"time = {time.time() - s}")
	#print(result)
	#print(result.oldFormat())
	#print(result.getCheckpointCount())

	print(result)


	# import numpy as np
	# numpy_array = np.array(result[:2])
	# df = pd.DataFrame(numpy_array.T, columns=['s_t', 's'])
	# df.to_csv('angles_ep5_bool.csv', index=False)

	# End the timer of the whole process
	# end = time.time()
	# print(f'time for the full operation: {end - start}s')


if __name__ == '__main__':
	# First is name of exec, second formula file, third signals input
	# Fourth is semantics specification (one of ['quantitative', 'boolean']), optional (default = quantitative)
	# Fifth is the algorithm used in quantitative semantics (one of ['efficient', 'syntax']), optional (default = efficient)
	print(len(sys.argv))
	print(sys.argv)
	for i in range(1, len(sys.argv)):
		sys.argv[i] = sys.argv[i].lower()
	if len(sys.argv) < 3:
		print("Expected at least two input parameters to this script: formula file and signal input file")
		exit(0)
	else:
		if len(sys.argv) == 3:
			sys.argv.append("quantitative")
		if len(sys.argv) >= 4:
			if sys.argv[3] not in ['quantitative', 'boolean']:
				print("Expected the semantic specification (third argument) to be either 'quantitative' or 'boolean'")
				exit(0)
			else:
				if len(sys.argv) == 4:
					sys.argv.append("efficient")
				if len(sys.argv) >= 5:
					if sys.argv[4] not in ['efficient', 'syntax']:
						print("Expected the algorithm specification (fourth argument) to be either 'efficient' or 'syntax'")
						exit(0)
					if len(sys.argv) > 5:
						print("Found more parameters than expected. Ignoring all parameters after the fourth.")
	main(formulafile=sys.argv[1], signalfile=sys.argv[2], semantics=sys.argv[3], algorithm=sys.argv[4])
	# main(sys.argv)
	#main(['', 'formula.stl', 'signals/ex_1c.csv', 'quantitative', 'efficient'])
