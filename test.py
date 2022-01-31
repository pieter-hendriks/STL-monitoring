import unittest

if __name__ == "__main__":
	# If no parameters, don't include cartpole
	# argv = sys.argv
	# sys.argv = [sys.argv[0]]
	# if len(argv) == 1:
	# 	argv.append('fast')
	# if argv[1] in ['fast', 'all']:
	# 	from test import QuantitativeSemanticsTest, BooleanSemanticsTest
	# if argv[1] in ['cartpole', 'all']:
	# 	from test import QuantitativeCartpoleTest, BooleanCartpoleTest
	# if argv[1] not in ['cartpole', 'all', 'fast']:
	# 	print("Invalid parameter passed.\nValid is no parameter(=fast), 'fast', 'all' or 'cartpole'.")
	# 	exit(1)
	from test.unitTests import *
	unittest.main()