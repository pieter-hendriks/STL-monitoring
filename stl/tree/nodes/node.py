""" Implement Node class """
# pylint: disable: missing-module-docstring
from typing import Union, List
# pylint: enable: missing-module-docstring
from ...signals import SignalList, Signal, BooleanSignal


class Node:  # Abstract class
	""" Base class representing nodes in the STL ASTs """
	count = 0  # Keep a number of the amount of nodes, also used to define ids

	def __init__(self) -> None:
		self.children: List['Node'] = []
		self.parent: 'Node' = None
		self.id: int = type(self).count  # Causes every node to be unique (handy for dot)
		type(self).count += 1  # Raise the counter every time

		# Location of the node in the formula for debugging purposes
		self.line: int = 0
		self.column: int = 0

		# For the creation of the tree, used in customStlListener
		self.doublePop: bool = False
		self.negateNext: bool = False

	# Add a childnode
	def add(self, node: 'Node') -> None:
		""" Adds a child node to the current node (end of the list). """
		self.children.append(node)
		self.children[-1].parent = self

	def name(self) -> str:
		""" Gets the node's name """
		return self.__class__.__name__.split('Node', maxsplit=1)[0]

	# Merge a node with this node
	def merge(self, node: 'Node') -> None:
		"""
		Removes other node from its parent's children list
		moves its children into this node's children list
		updates parent in node's children to self.
		"""
		node.parent.children.remove(node)
		self.children = node.children + self.children
		for child in node.children:
			child.parent = self

	# Execute the (stl) node
	# Expects a pandas dataframe with the signals
	# Expects a string with the type of semantic that will be used
	# returns a single signal or number
	# pylint: disable=no-self-use
	def validate(self,
	             signals: SignalList,
	             semantic: str = 'quantitative',
	             plot: bool = False) -> Union[Signal, BooleanSignal]:
		"""
		Compute the robustness for this node; semantic parameter respected.

		Throws if not overridden by derived class.
		"""
		raise RuntimeError("Base Node validate() called.")

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		""" Compute the quantitative validation for this node (and its children) """
		raise RuntimeError("Base quant validate")

	def booleanValidate(self, signals: SignalList, plot: bool, booleanize=False) -> BooleanSignal:
		""" Compute the boolean validation for this node (and its children) """
		raise RuntimeError("Base bool validate")

	# Processes the token (terminal node in ANTLR AST)
	def processToken(self, token: str) -> None:
		""" Read in a token for this node. Different tokens may lead to different behaviour. """
		# Empty function to be overridden in derived classes which handle tokens
		# Some tokens don't require any behaviour, so we can just have an empty function here.

	# pylint: enable=no-self-use

	# To know how many plots will be made
	def calculatePlotAmount(self) -> int:
		""" Computes the amount of plots required to plot the results of this node and its children. """
		return sum([x.calculatePlotAmount() for x in self.children])

	def text(self) -> str:
		""" Get the textual representation for this node """
		return self.name()

	def dotRepresentation(self) -> str:
		""" Get the dot representation for this node """
		return '\t"' + self.name() + '_' + str(self.id) + '"[label="' + self.text() + '"];\n'

	def toDot(self, file) -> None:
		""" Convert this node toDot lang """
		if self.parent is None:
			file.write("digraph stlTree {\n")
			file.write(self.dotRepresentation())
		else:
			file.write(self.dotRepresentation())
			file.write(
			    '\t"' + self.parent.name() + '_' + str(self.parent.id) + '" -> "' + self.name() + '_' + str(self.id) + '";\n'
			)

		for child in self.children:
			child.toDot(file)
		if self.parent is None:
			file.write("}")

	# # Check if two nodes in the AST can merge
	# def canMerge(self, node):
	#     return node.__class__ == self.__class__
