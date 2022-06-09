import unittest

from antlr4.tree.Tree import ParseTreeWalker
from ..data import signalFiles, expectedOutput
from stl.parsing import CustomStlListener, stlLexer, stlParser
from antlr4 import CommonTokenStream, ParseTreeWalker, InputStream
from stl.signals import SignalList

class BooleanSemanticsTest(unittest.TestCase):
	def setUp(self):
		self.formula = InputStream('[]{0,10}((p>0)-><>{1,2}(q>0))')
		lexer = stlLexer(self.formula)
		stream = CommonTokenStream(lexer)
		parser = stlParser(stream)
		tree = parser.content()
		listener = CustomStlListener()
		walker = ParseTreeWalker()
		walker.walk(listener, tree)
		parser.addParseListener(listener)
		self.stlTree = listener.stlTree

	def testValidatedSignal(self):
		signal = SignalList.fromCSV(signalFiles.booleanValidatedSignal)
		result = self.stlTree.validate(signal, 'boolean', plot=False)
		self.assertEqual(expectedOutput.booleanValidatedSignal, result.oldFormat(), f"Boolean validated signal result mismatch for input {signalFiles.booleanValidatedSignal} (validated signal)")

	def testInvalidatedSignal(self):
		signal = SignalList.fromCSV(signalFiles.booleanInvalidatedSignal)
		result = self.stlTree.validate(signal, 'boolean', plot=False)
		self.assertEqual(expectedOutput.booleanInvalidatedSignal, result.oldFormat(), f"Boolean invalidated signal result mismatch for input {signalFiles.booleanInvalidatedSignal} (invalidated signal)")



class BooleanCartpoleTest(unittest.TestCase):
	def setUp(self):
		self.formula = InputStream('[]{0, 2770}(((|e5|) < 12) & ((|e5| > 4.5) -> <>{0,150}[]{0,30}(|e5|<=4.5)))')
		lexer = stlLexer(self.formula)
		stream = CommonTokenStream(lexer)
		parser = stlParser(stream)
		tree = parser.content()
		listener = CustomStlListener()
		walker = ParseTreeWalker()
		walker.walk(listener, tree)
		parser.addParseListener(listener)
		self.stlTree = listener.stlTree

	def testValidatedSignal(self):
		signal = SignalList.fromCSV(signalFiles.cartpoleBooleanSignal, forceBooleanSemantics=True)
		result = self.stlTree.validate(signal, 'boolean', plot=False)
		self.assertEqual(expectedOutput.booleanCartpoleSignal, result.oldFormat(), "Boolean cartpole result mismatch.")


class BooleanCartpoleWrongFormulaTest(unittest.TestCase):
	def setUp(self):
		self.formula = InputStream('[]{150,2950}(((|e5|) < 12) & ((|e5| > 4.5) -> <>{0,150}[]{0,30}(|e5|<=4.5)))')
		lexer = stlLexer(self.formula)
		stream = CommonTokenStream(lexer)
		parser = stlParser(stream)
		tree = parser.content()
		listener = CustomStlListener()
		walker = ParseTreeWalker()
		walker.walk(listener, tree)
		parser.addParseListener(listener)
		self.stlTree = listener.stlTree

	def testValidatedSignal(self):
		signal = SignalList.fromCSV(signalFiles.cartpoleBooleanSignal, forceBooleanSemantics=True)
		result = self.stlTree.validate(signal, 'boolean', plot=False)
		self.assertEqual([[], [], []], result.oldFormat(), "Boolean cartpole result mismatch.")

if __name__=='__main__':
	unittest.main()