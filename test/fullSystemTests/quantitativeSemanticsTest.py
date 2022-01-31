import unittest

from antlr4.tree.Tree import ParseTreeWalker
from ..data import *
from stl.parsing import CustomStlListener, stlLexer, stlParser
from antlr4 import CommonTokenStream, ParseTreeWalker, InputStream
from stl.signals import SignalList


class QuantitativeSemanticsTest(unittest.TestCase):
	def setUp(self):
		self.formula = InputStream('[]{0,300}(x1-><>{3,5}x2)')
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
		signal = SignalList.fromCSV(signalFiles.quantitativeValidatedSignal)
		result = self.stlTree.validate(signal, 'quantitative', plot=False)
		self.assertEqual(expectedOutput.quantitativeValidatedSignal, result, f"Quantitative semantics result mismatch for input {signalFiles.quantitativeValidatedSignal} (validated signal)")

	def testInvalidatedSignal(self):
		signal = SignalList.fromCSV(signalFiles.quantitativeInvalidatedSignal)
		result = self.stlTree.validate(signal, 'quantitative', plot=False)
		self.assertEqual(expectedOutput.quantitativeInvalidatedSignal, result, f"Quantitative semantics result mismatch for input {signalFiles.quantitativeInvalidatedSignal} (invalidated signal)")
	
class QuantitativeCartpoleTest(unittest.TestCase):
	def setUp(self):
		self.formula = InputStream('[]{150,2950}(((12 - |e5|)) & ((|e5| - 4.5) -> <>{0,150}[]{0,30}(4.5 - |e5|)))')
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
		signal = SignalList.fromCSV(signalFiles.cartpoleQuantitativeSignal)
		result = self.stlTree.validate(signal, 'quantitative', plot=False)
		self.assertEqual(expectedOutput.quantitativeCartpoleSignal, result, "Quantitative cartpole result mismatch.")

if __name__=='__main__':
	unittest.main()