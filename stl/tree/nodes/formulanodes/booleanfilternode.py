
from .formulanode import FormulaNode
from stl.stlUtils import getPunctualIntersection
from numbers import Number
import warnings
import numpy
from ....signals import Signal, BooleanSignal, SignalList

class BooleanFilterNode(FormulaNode):
	OPERATORS = {
    '=': lambda x, y: x == y,
    '!=': lambda x, y: x != y,
    '>=': lambda x, y: x >= y,
    '<=': lambda x, y: x <= y,
    '>': lambda x, y: x > y,
    '<': lambda x, y: x < y
}
	def __init__(self) -> None:
		super().__init__()
		self.filter = None

	def processToken(self, token: str) -> None:
		self.filter = str(token)

	def booleanValidate(self, signals: SignalList, plot: bool) -> BooleanSignal:
		# TODO: Verify that this isn't a problem. It appears Boolean filter node is just all the comparison operators?
		# If so, rename to "ComparisonOperatorNode" may be a sensible improvement
		# warnings.warn("Using boolean semantics for boolean filter node.")
		print(type(self.children[0]), type(self.children[1]))
		result = [self.children[0].booleanValidate(signals, plot), self.children[1].booleanValidate(signals, plot)]
		temp = Signal()
		if isinstance(result[0], Signal) and isinstance(result[1], Signal):
			result = getPunctualIntersection(result[0], result[1], 'boolean')
			for i in range(result[0].getCheckpointCount()):
				temp.emplaceCheckpoint(result[0].getTime(i), int(self.OPERATORS[self.filter](result[0].getValue(i), result[1].getValue(i))))
		elif isinstance(result[0], Signal) and isinstance(result[1], Number):
			temp = Signal("booleanfilterresult", result[0].getTimes(), [int(self.OPERATORS[self.filter](x, result[1])) for x in result[0].getValues()])
			# temp += [result[0][0], [int(self.OPERATORS[self.filter](x, result[1])) for x in result[0][1]]]
		else:
			raise Exception(f'Encountered a BooleanFilter of unknown types {type(result[0])} and {type(result[1])}')
		if plot:
			self.booleanPlot(temp)
		return temp  # signal represented as (t, y <, dy>)

	def quantitativeValidate(self, signals: SignalList, plot: bool) -> Signal:
		warnings.warn("Using quantitative semantics for boolean filter node.")
		result = [self.children[0].quantitativeValidate(signals, plot), self.children[1].quantitativeValidate(signals, plot)]
		temp = []
		if isinstance(result[0], list) and isinstance(result[1], list):
			result = list(getPunctualIntersection(result[0], result[1], 'quantitative'))
			temp += [[], []]
			for i in range(len(result[0][0])):
				temp[0].append(result[0][0][i])
				temp[1].append(int(self.OPERATORS[self.filter](result[0][1][i], result[1][1][i])))
		elif isinstance(result[0], list) and isinstance(result[1], Number):
			temp += [result[0][0], [int(self.OPERATORS[self.filter](x, result[1])) for x in result[0][1]]]
		else:
			raise Exception(f'Encountered a BooleanFilter of unknown types {type(result[0])} and {type(result[1])}')

		# Calculation of the derivative
		dydx = numpy.diff(temp[1]) / numpy.diff(temp[0])
		temp += [list(dydx) + [0]]
		if plot:
			self.quantitativePlot(signals)
		return temp  # signal represented as (t, y <, dy>)

	def text(self) -> str:
		return 'BooleanFilter' + ' [' + str(self.id) + ']: ' + self.filter
