from ...signals import SignalList, Signal, BooleanSignal
from typing import Union, List

class Node:  # Abstract class
	count = 0  # Keep a number of the amount of nodes, also used to define ids

	def __init__(self) -> None:
		self.children: List['Node'] = []
		self.parent: 'Node' = None
		self.id: int= type(self).count  # Causes every node to be unique (handy for dot)
		type(self).count += 1  # Raise the counter every time

		# Location of the node in the formula for debugging purposes
		self.line: int = 0
		self.column: int = 0

		# For the creation of the tree, used in customStlListener
		self.doublePop: bool = False
		self.negateNext: bool = False

	# Add a childnode
	def add(self, node: 'Node') -> None:
		self.children.append(node)
		self.children[-1].parent = self

	def name(self) -> str:
		return self.__class__.__name__.split('Node')[0]

	# Merge a node with this node
	def merge(self, node: 'Node') -> None:
		node.parent.children.remove(node)
		self.children = node.children + self.children
		for child in node.children:
			child.parent = self

	# Execute the (stl) node
	# Expects a pandas dataframe with the signals
	# Expects a string with the type of semantic that will be used
	# returns a single signal or number
	def validate(self, signals: SignalList, semantic: str='quantitative', plot: bool=False) -> Union[Signal, BooleanSignal]:
		if semantic == 'quantitative':
			return self.quantitativeValidate(signals, plot)
		elif semantic == 'boolean':
			return self.booleanValidate(signals, plot)
		else:
			raise RuntimeError(f"Unknown semantic: {semantic}")

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		raise RuntimeError("Base quant validate")

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		raise RuntimeError("Base bool validate")

	# To know how many plots will be made
	def calculatePlotAmount(self) -> int:
		return sum([x.calculatePlotAmount() for x in self.children]) + 0

	# Processes the token (terminal node in ANTLR AST)
	def processToken(self, token: str) -> None:
		# Empty function to be overridden in derived classes which handle tokens
		pass

	def text(self) -> str:
		return self.name()

	def dotRepresentation(self) -> str:
		return '\t"' + self.name() + '_' + str(self.id) + '"[label="' + self.text() + '"];\n'

	def toDot(self, file) -> None:
		if self.parent is None:
			file.write("digraph stlTree {\n")
			file.write(self.dotRepresentation())
		else:
			file.write(self.dotRepresentation())
			file.write('\t"' + self.parent.name() + '_' + str(self.parent.id) + '" -> "' + self.name() + '_' + str(self.id) + '";\n')

		for child in self.children:
			child.toDot(file)
		if self.parent is None:
			file.write("}")

	# # Check if two nodes in the AST can merge
	# def canMerge(self, node):
	#     return node.__class__ == self.__class__