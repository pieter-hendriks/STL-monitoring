""" Main """
# pylint: disable-all
import unittest
if __name__ == "__main__":
	from test.unitTests import *
	try:
		unittest.main()
	except SystemExit:
		exit(0)