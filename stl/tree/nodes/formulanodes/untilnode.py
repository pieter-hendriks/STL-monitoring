""" Implementation of the Until AST node for STL tool """
from .formulanode import FormulaNode
from ....utility import Interval
from ....signals import Signal, BooleanSignal, SignalList
from ....operators import computeTimedEventually, computeUntimedEventually, computeTimedUntil
from ....operators import computeUntimedUntil, computeSyntaxUntil, computeBooleanUntil


class UntilNode(FormulaNode):
	""" Node representing the Until operation in STL formulas """

	def __init__(self) -> None:
		super().__init__()
		self.useEfficientAlgorithm()
		# self.useSyntaxAlgorithm()

	def useSyntaxAlgorithm(self):
		""" Sets the Until node to use the Syntax (inefficient) algorithm implementation. """
		self.__useSyntaxAlgorithm = True

	def useEfficientAlgorithm(self):
		""" Sets the Until node to use the efficient algorithm implementation. """
		self.__useSyntaxAlgorithm = False

	def __handleEfficientAlgorithm(self, signals: SignalList, plot: bool) -> Signal:
		""" Prepares the data for use with the efficient algorithm and then calls the operation """
		if len(self.children) in [2, 4]:
			childSignals = SignalList(
			    self.children[0].quantitativeValidate(signals, plot), self.children[-1].quantitativeValidate(signals, plot)
			)
		if len(self.children) == 1:
			# Untimed eventually -- no time interval children, 1 signal child
			result = computeUntimedEventually(self.children[0].quantitativeValidate(signals, plot))
		elif len(self.children) == 2:
			# Untimed Until -- no time interval children, 2 signal children (can't have time, no signal)
			result = computeUntimedUntil(childSignals[0], childSignals[1])
		elif len(self.children) >= 3:
			interval: Interval = Interval(
			    self.children[-3].quantitativeValidate(signals, plot).getValue(0),
			    self.children[-2].quantitativeValidate(signals, plot).getValue(0)
			)
			if len(self.children) == 4:  # timed until, 2 time interval children, 2 signal children
				result = computeTimedUntil(childSignals[0], childSignals[1], interval)
			else:
				# Timed eventually - 2 time interval children, 1 signal child (time can't have 1 child, so only option)
				result = computeTimedEventually(self.children[-1].quantitativeValidate(signals, plot), interval)
		return result

	def __handleSyntaxAlgorithm(self, signals: SignalList, plot: bool) -> Signal:
		""" Prepares the data for use with the syntax algorithm and then calls the operation """
		# If we have four children, we have a timed until operation (lhs, interval (lower & upper), rhs)
		if len(self.children) == 4:
			childResults: SignalList = SignalList(
			    self.children[0].quantitativeValidate(signals, plot), self.children[3].quantitativeValidate(signals, plot)
			)
			name = "timedUntil"
		# If we have three children, we have a timed eventually operation (interval (lower & upper), rhs)
		elif len(self.children) == 3:
			childResults: SignalList = SignalList([
			    Signal.createConstant('DummyTrueSignal', 1), self.children[2].quantitativeValidate(signals, plot)
			])
			name = "timedEventually"
		# If we have two children, we have an untimed until operation (lhs, rhs)
		elif len(self.children) == 2:
			childResults: SignalList = SignalList(
			    self.children[0].quantitativeValidate(signals, plot), self.children[1].quantitativeValidate(signals, plot)
			)
			name = "untimedUntil"
		# Else we must have 1 child, which is the untimed eventually operation (rhs)
		else:
			assert len(self.children) == 1, "Invalid amount of children for until node."
			childResults: SignalList = SignalList(
			    Signal.createConstant('DummyTrueSignal', 1), self.children[0].quantitativeValidate(signals, plot)
			)
			name = "untimedEventually"
		# Get the interval limit values for the interval [a, b]
		# Untimed operation
		aSignal: Signal = Signal.createConstant('a', 0)
		bSignal: Signal = Signal.createConstant('b', float('inf'))
		if len(self.children) >= 3:
			# Timed operation
			aSignal: Signal = self.children[-3].quantitativeValidate(signals, plot)
			bSignal: Signal = self.children[-2].quantitativeValidate(signals, plot)

		assert all(x == s.getValue(0) for s in [aSignal, bSignal] for x in s.getValues())
		interval = Interval(aSignal.getValue(0), bSignal.getValue(0))
		result = computeSyntaxUntil(childResults[0], childResults[1], interval)
		result.setName(name)
		return result

	def quantitativeValidate(self, signals: SignalList, plot: bool = False) -> Signal:
		if not self.__useSyntaxAlgorithm:
			result: Signal = self.__handleEfficientAlgorithm(signals, plot)
		else:
			result: Signal = self.__handleSyntaxAlgorithm(signals, plot)
		result.recomputeDerivatives()
		self.quantitativePlot(plot, result)
		return result

	def booleanValidate(self, signals: SignalList, plot: bool, booleanize=False) -> BooleanSignal:
		# Operator can be unary or binary;
		# Children are 2 integers from the time interval, plus one or two formulas.
		if len(self.children) == 4:
			childResults: SignalList = SignalList(
			    [self.children[0].booleanValidate(signals, plot, True), self.children[3].booleanValidate(signals, plot, True)]
			)
		else:
			assert len(self.children) == 3
			childResult: BooleanSignal = self.children[2].booleanValidate(signals, plot, True)
			dummySignal: BooleanSignal = BooleanSignal(
			    "DummyTrueSignal", childResult.getTimes(), [1] * childResult.getCheckpointCount(),
			    [0] * childResult.getCheckpointCount()
			)
			childResults: SignalList = SignalList([dummySignal, childResult])
		childResults = SignalList(BooleanSignal.computeComparableSignals(childResults[0], childResults[1]))
		# Don't booleanize these, the interval is supposed to be real numbers. It's a time interval, not a signal value.
		interval = Interval(self.children[-3].booleanValidate(signals, plot).getValue(0), self.children[-2].booleanValidate(signals, plot).getValue(0))
		until = computeBooleanUntil(childResults[0], childResults[1], interval)
		self.booleanPlot(plot, until)
		if booleanize:
			return BooleanSignal.fromSignal(until)
		return until
