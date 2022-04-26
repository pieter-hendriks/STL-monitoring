# pylint: disable-all
from lib2to3.pytree import convert
import os
import sys
import cProfile
import pstats
import random
from unittest import mock

print(os.getcwd())
sys.path.insert(0, os.getcwd() + '/stlTool')
from stl.signals import Signal
from stl.tree import ContentNode, UntilNode

FILE_PREFIX = "stlTool/examples/ritamtest/"
# Size in counts
TIME_MAX = 1000
SIGNAL_MAGNITUDE = 250
# Best to lower SIGNAL_SIZE (and maybe INTERVAL_UB) if efficient == False,
# Syntax algorithm is significantly slower.
EFFICIENT = False
SIMPLE = True

for SIGNAL_SIZE in [2500, 5000]:  #, 5000, 10000, 20000, 40000, 80000]:
	for INTERVAL_UB in [10]:  #, 200]:  # LB is always zero - minor modifications may be needed if it should be modified.
		FILENAME = f"{FILE_PREFIX}{INTERVAL_UB}_{SIGNAL_SIZE}_{'efficient' if EFFICIENT else 'syntax'}_{'simple' if SIMPLE else 'complex'}_stats"
		random.seed(1)

		# Create some formula manually
		def createSimpleFormula():
			root: ContentNode = ContentNode()
			operator: UntilNode = UntilNode()
			root.children = [operator]
			lhsSignal: mock.Mock = mock.Mock()
			rhsSignal: mock.Mock = mock.Mock()
			intervalLower: mock.Mock = mock.Mock()
			intervalUpper: mock.Mock = mock.Mock()
			# Round random values to 3 decimals to avoid precision errors
			s1values = [round((random.random() - 0.5) * SIGNAL_MAGNITUDE * 2, 3) for _ in range(SIGNAL_SIZE)]
			s2values = [round((random.random() - 0.5) * SIGNAL_MAGNITUDE * 2, 3) for _ in range(SIGNAL_SIZE)]
			# Create timestamps in the range [0, TIME_MAX], but increase stamp count in that range as SIGNAL_SIZE increases
			times = [(x*TIME_MAX) / SIGNAL_SIZE for x in range(SIGNAL_SIZE)]
			convertedUB = (INTERVAL_UB*TIME_MAX) / SIGNAL_SIZE  # Have interval match modified timestamps
			# Set returns on the mocks
			lhsSignal.quantitativeValidate.return_value = Signal('lhs', times, s1values)
			rhsSignal.quantitativeValidate.return_value = Signal('rhs', times, s2values)
			intervalLower.quantitativeValidate.return_value = Signal.createConstant('LB', 0)
			intervalUpper.quantitativeValidate.return_value = Signal.createConstant('UB', convertedUB)
			# Set the children for our Until node
			operator.children = [lhsSignal, intervalLower, intervalUpper, rhsSignal]
			# Use the correct algorithm
			if EFFICIENT:
				operator.useEfficientAlgorithm()
			else:
				operator.useSyntaxAlgorithm()
			return root

		if SIMPLE:
			stlTreeRoot = createSimpleFormula()
		else:
			raise RuntimeError("Complex formula not implemented!")

		def evaluate():
			result = stlTreeRoot.validate(None, 'quantitative', False)

		# Profiling introduces some overhead,
		# but relative performance between two profiled cases should be comparable
		cProfile.run("evaluate()", FILENAME)
		pstats.Stats(FILENAME).sort_stats("cumtime").print_stats().sort_stats("tottime").print_stats(5)
