""" Main """
# pylint: disable-all
import os
os.chdir('stlTool')
import unittest
if __name__ == "__main__":
	from tests import *
	try:
		unittest.main()
	except SystemExit:
		exit(0)