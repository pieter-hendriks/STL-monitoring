""" Custom STL Listener implementation """
from antlr4 import TerminalNode
from stl.parsing.stlListener import stlListener
from stl.tree import FormulaNode, NegationNode, FloatValueNode, AbsoluteValueNode
from stl.tree import AndNode, BinaryOperationNode, ComparisonOperatorNode, ContentNode
from stl.tree import IntValueNode, QuantitativeSignalNode, SignalNode, UntilNode

if __name__ is not None and "." in __name__:
	from .stlParser import stlParser
else:
	from stl.parsing.stlParser import stlParser


# This class defines a complete listener for a parse tree produced by stlParser.
# pylint: disable=too-many-public-methods
class CustomStlListener(stlListener):
	""" Custom listener for STL parse tree. """

	def __init__(self):
		self.stlTree = None

	# Split the tree, a.k.a. add a child = branch
	def generateBranch(self, node, context):
		""" Add a new child in the STL AST """
		implicaton = False
		# If former is an implication
		if self.stlTree.negateNext == 2 and isinstance(node, FormulaNode):
			self.stlTree.negateNext = False  # First formula can't be negated
			implicaton = True

		# If the former type of node needs the its children to be negated
		if self.stlTree.negateNext and isinstance(node, FormulaNode):
			self.stlTree.negateNext = False  # Make false to avoid inf loop
			self.generateBranch(NegationNode(), context)  # Add the negation node
			self.stlTree.parent.negateNext = True  # Don't forget to make it true again (now one node further so parent)
			self.stlTree.doublePop = True  # Two nodes added, so two nodes have to be popped later (recursive behaviour)

		if implicaton:  # Make sure the next is negated
			self.stlTree.negateNext = True

		# Location of the node in the formula for debugging purposes
		node.line = context.start.line
		node.column = context.start.column

		# Add the new node and make the current tree the new branch (recursive behavior)
		self.stlTree.add(node=node)
		self.stlTree = node

	# If the node is a terminal node meaning a token
	def visitTerminal(self, node: TerminalNode):
		""" Visit a terminal node (token) in tree """
		token = str(node)

		if token in '[]{}();,':  # Ignore these tokens
			return
		self.stlTree.processToken(token)  # Put the value of the token into a variable to use later on

	# Go back up the tree
	def popStack(self):
		""" Go back up one level in the tree """
		# If node = negation and child too -> simplify
		if isinstance(self.stlTree, NegationNode) and isinstance(self.stlTree.children[0], NegationNode):
			self.stlTree.parent.add(self.stlTree.children[0].children[0])
			self.stlTree.parent.children.remove(self.stlTree)
			self.stlTree.children[0].children[0].parent = self.stlTree.parent

		# Go back to the parent of the node
		if self.stlTree.parent is not None:
			self.stlTree = self.stlTree.parent

		# If a double pop is necessary (when two nodes were added)
		if self.stlTree.doublePop:
			self.stlTree.doublePop = False
			self.popStack()

	# Enter a parse tree produced by stlParser#content.
	def enterContent(self, ctx: stlParser.ContentContext):
		if self.stlTree is None:
			self.stlTree = ContentNode()

	# Exit a parse tree produced by stlParser#content.
	def exitContent(self, ctx: stlParser.ContentContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#always.
	def enterTimedAlways(self, ctx: stlParser.TimedAlwaysContext):  # □a := ¬◊¬a := ¬(true U ¬a)
		self.generateBranch(NegationNode(), ctx)
		self.generateBranch(UntilNode(), ctx)
		self.stlTree.negateNext = True  # Indicate that the formula children of the until node have to be negated

	# Exit a parse tree produced by stlParser#always.
	def exitTimedAlways(self, ctx: stlParser.TimedAlwaysContext):
		self.popStack()  # Leave the Until node
		self.popStack()  # Leave the Negation node

	# Enter a parse tree produced by stlParser#always.
	def enterUntimedAlways(self, ctx: stlParser.UntimedAlwaysContext):  # □a := ¬◊¬a := ¬(true U ¬a)
		self.generateBranch(NegationNode(), ctx)
		self.generateBranch(UntilNode(), ctx)
		self.stlTree.negateNext = True  # Indicate that the formula children of the until node have to be negated

	# Exit a parse tree produced by stlParser#always.
	def exitUntimedAlways(self, ctx: stlParser.UntimedAlwaysContext):
		self.popStack()  # Leave the Until node
		self.popStack()  # Leave the Negation node

	# Enter a parse tree produced by stlParser#booleanFilter.
	def enterBooleanFilter(self, ctx: stlParser.BooleanFilterContext):
		self.generateBranch(ComparisonOperatorNode(), ctx)

	# Exit a parse tree produced by stlParser#booleanFilter.
	def exitBooleanFilter(self, ctx: stlParser.BooleanFilterContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#negation.
	def enterNegation(self, ctx: stlParser.NegationContext):
		self.generateBranch(NegationNode(), ctx)

	# Exit a parse tree produced by stlParser#negation.
	def exitNegation(self, ctx: stlParser.NegationContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#or.
	def enterOr(self, ctx: stlParser.OrContext):  # a∨b := ¬(¬a∧¬b)
		self.generateBranch(NegationNode(), ctx)
		self.generateBranch(AndNode(), ctx)
		self.stlTree.negateNext = True  # Indicate that the formula children of the and node have to be negated

	# Exit a parse tree produced by stlParser#or.
	def exitOr(self, ctx: stlParser.OrContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#quantitativeSignal.
	def enterQuantitativeSignal(self, ctx: stlParser.QuantitativeSignalContext):
		self.generateBranch(QuantitativeSignalNode(), ctx)

	# Exit a parse tree produced by stlParser#quantitativeSignal.
	def exitQuantitativeSignal(self, ctx: stlParser.QuantitativeSignalContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#and.
	def enterAnd(self, ctx: stlParser.AndContext):
		self.generateBranch(AndNode(), ctx)

	# Exit a parse tree produced by stlParser#and.
	def exitAnd(self, ctx: stlParser.AndContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#implication.
	def enterImplication(self, ctx: stlParser.ImplicationContext):  # a→b := ¬a∨b := ¬(a∧¬b)
		self.generateBranch(NegationNode(), ctx)
		self.generateBranch(AndNode(), ctx)
		self.stlTree.negateNext = 2  # Indicate that the second child of the and node has to be negated

	# Exit a parse tree produced by stlParser#implication.
	def exitImplication(self, ctx: stlParser.ImplicationContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#scope.
	def enterScope(self, ctx: stlParser.ScopeContext):  # Only here to make the tree in the right shape
		pass

	# Exit a parse tree produced by stlParser#scope.
	def exitScope(self, ctx: stlParser.ScopeContext):  # Only here to make the tree in the right shape
		pass

	# Enter a parse tree produced by stlParser#eventually.
	def enterTimedEventually(self, ctx: stlParser.TimedEventuallyContext):  # ◊a := true U a
		self.generateBranch(UntilNode(), ctx)

	# Exit a parse tree produced by stlParser#eventually.
	def exitTimedEventually(self, ctx: stlParser.TimedEventuallyContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#eventually.
	def enterUntimedEventually(self, ctx: stlParser.UntimedEventuallyContext):  # ◊a := true U a
		self.generateBranch(UntilNode(), ctx)

	# Exit a parse tree produced by stlParser#eventually.
	def exitUntimedEventually(self, ctx: stlParser.UntimedEventuallyContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#until.
	def enterTimedUntil(self, ctx: stlParser.TimedUntilContext):
		self.generateBranch(UntilNode(), ctx)

	# Exit a parse tree produced by stlParser#until.
	def exitTimedUntil(self, ctx: stlParser.TimedUntilContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#until.
	def enterUntimedUntil(self, ctx: stlParser.UntimedUntilContext):
		self.generateBranch(UntilNode(), ctx)

	# Exit a parse tree produced by stlParser#until.
	def exitUntimedUntil(self, ctx: stlParser.UntimedUntilContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#signalExpressionScope.
	def enterSignalExpressionScope(
	    self, ctx: stlParser.SignalExpressionScopeContext
	):  # Only here to make the tree in the right shape
		pass

	# Exit a parse tree produced by stlParser#signalExpressionScope.
	def exitSignalExpressionScope(
	    self, ctx: stlParser.SignalExpressionScopeContext
	):  # Only here to make the tree in the right shape
		pass

	# Enter a parse tree produced by stlParser#signalProduct.
	def enterSignalProduct(self, ctx: stlParser.SignalProductContext):
		self.generateBranch(BinaryOperationNode(), ctx)

	# Exit a parse tree produced by stlParser#signalProduct.
	def exitSignalProduct(self, ctx: stlParser.SignalProductContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#signalSum.
	def enterSignalSum(self, ctx: stlParser.SignalSumContext):
		self.generateBranch(BinaryOperationNode(), ctx)

	# Exit a parse tree produced by stlParser#signalSum.
	def exitSignalSum(self, ctx: stlParser.SignalSumContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#signalAbsolute.
	def enterSignalAbsolute(self, ctx: stlParser.SignalAbsoluteContext):
		self.generateBranch(AbsoluteValueNode(), ctx)

	# Exit a parse tree produced by stlParser#signalAbsolute.
	def exitSignalAbsolute(self, ctx: stlParser.SignalAbsoluteContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#signalSignal.
	def enterSignalSignal(self, ctx: stlParser.SignalSignalContext):
		self.generateBranch(SignalNode(), ctx)

	# Exit a parse tree produced by stlParser#signalSignal.
	def exitSignalSignal(self, ctx: stlParser.SignalSignalContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#product.
	def enterProduct(self, ctx: stlParser.ProductContext):
		self.generateBranch(BinaryOperationNode(), ctx)

	# Exit a parse tree produced by stlParser#product.
	def exitProduct(self, ctx: stlParser.ProductContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#absolute.
	def enterAbsolute(self, ctx: stlParser.AbsoluteContext):
		self.generateBranch(AbsoluteValueNode(), ctx)

	# Exit a parse tree produced by stlParser#absolute.
	def exitAbsolute(self, ctx: stlParser.AbsoluteContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#sum.
	def enterSum(self, ctx: stlParser.SumContext):
		self.generateBranch(BinaryOperationNode(), ctx)

	# Exit a parse tree produced by stlParser#sum.
	def exitSum(self, ctx: stlParser.SumContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#expressionScope.
	def enterExpressionScope(
	    self, ctx: stlParser.ExpressionScopeContext
	):  # Only here to make the tree in the right shape
		pass

	# Exit a parse tree produced by stlParser#expressionScope.
	def exitExpressionScope(self, ctx: stlParser.ExpressionScopeContext):  # Only here to make the tree in the right shape
		pass

	# Enter a parse tree produced by stlParser#value.
	def enterValue(self, ctx: stlParser.ValueContext):  # Only here to make the tree in the right shape
		pass

	# Exit a parse tree produced by stlParser#value.
	def exitValue(self, ctx: stlParser.ValueContext):  # Only here to make the tree in the right shape
		pass

	# Enter a parse tree produced by stlParser#signal.
	def enterSignal(self, ctx: stlParser.SignalContext):
		self.generateBranch(SignalNode(), ctx)

	# Exit a parse tree produced by stlParser#signal.
	def exitSignal(self, ctx: stlParser.SignalContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#constant.
	def enterConstant(self, ctx: stlParser.ConstantContext):  # Only here to make the tree in the right shape
		pass

	# Exit a parse tree produced by stlParser#constant.
	def exitConstant(self, ctx: stlParser.ConstantContext):  # Only here to make the tree in the right shape
		pass

	# Enter a parse tree produced by stlParser#intValue.
	def enterIntValue(self, ctx: stlParser.IntValueContext):
		self.generateBranch(IntValueNode(), ctx)

	# Exit a parse tree produced by stlParser#intValue.
	def exitIntValue(self, ctx: stlParser.IntValueContext):
		self.popStack()

	# Enter a parse tree produced by stlParser#floatValue.
	def enterFloatValue(self, ctx: stlParser.FloatValueContext):
		self.generateBranch(FloatValueNode(), ctx)

	# Exit a parse tree produced by stlParser#floatValue.
	def exitFloatValue(self, ctx: stlParser.FloatValueContext):
		self.popStack()
