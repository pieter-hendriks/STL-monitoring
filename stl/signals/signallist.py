from .signal import Signal
from typing import List
from .booleansignal import BooleanSignal
import pandas as pd

class SignalList(List[Signal]):
	# A class for managing a list of Signals.

	# Init is handled by List, so just pass-through
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)

	# TODO: Optimisation? Is switching to sorted list worth? For now, no performance issues.
	def getByName(self, name: str) -> Signal:
		signal: Signal
		for signal in self:
			if signal.getName() == name:
				return signal
		raise RuntimeError(F"Signal with name '{name}' not found.")
		
	@classmethod
	def fromCSV(cls, csv: str) -> 'SignalList':
		# Read Signals from CSV, return a SignalList instance
		# Column names in CSV should be 's', 's_t' and 's_d' for signal s (s must not contain '_')
		data = pd.read_csv(csv)
		colTitles = data.columns.values
		# Ensure columns are named correctly
		_verifyTitleNaming(colTitles)
		# Get the data from the dataframe
		signals, timestamps, derivatives = _findSignalColumns(colTitles), _findTimestampColumns(colTitles), _findDerivativeColumns(colTitles)
		_verifyColumns(signals, timestamps, derivatives, colTitles)
		# If we only have Boolean values, use the BooleanSignal class to initialize
		signalDataType = BooleanSignal if _isAllBooleanSignals(signals) else Signal
		ret = []
		for signal in signals:
			# Pattern as expected (and verified), read from dataframe into list of Signals
			timestamp = signal + '_t'
			derivative = signal + '_d'
			# Add Signal to the list
			if len(derivatives) != 0:
				ret.append(signalDataType(signal, list(data.loc[:,timestamp]), list(data.loc[:, signal]), list(data.loc[:,derivative])))
			else:
				ret.append(signalDataType(signal, list(data.loc[:,timestamp]), list(data.loc[:,signal])))
		return SignalList(ret)


# Helper functions for input handling


def _isAllBooleanSignals(signals: List[List[float]]) -> bool:
	return all([all([x == 1 or x == 0 for x in signal]) for signal in signals])


def _findSignalColumns(colTitles: List[str]) -> List[str]:
	return _findAllMatchingPattern(colTitles, '_', invertCondition = True)

# Timestamps must be labeled 'x_t' for any signal x
def _findTimestampColumns(colTitles: List[str]) -> List[str]:
	return _findAllMatchingPattern(colTitles, '_t')
	
# Derivatives must be labeled 'x_d' for any signal x
def _findDerivativeColumns(colTitles: List[str]) -> List[str]:
	return _findAllMatchingPattern(colTitles, '_d')
	
def _findAllMatchingPattern(collection: List[str], pattern: str, invertCondition: bool = False) -> List[str]:
	if invertCondition:
		return [c for c in collection if pattern not in c]
	return [c for c in collection if pattern in c]
	
def _verifyTitleNaming(titles: List[str]) -> None:
	# Underscores may only be followed by 'd' and 't', and that must be the end of the string.
	for title in titles:
		try:
			underscore = title.rindex('_')
		except ValueError:
		# Titles with no underscores present are allowed
			continue
		assert title[underscore + 1] in ['d', 't'], "Underscore must be followed by either 'd' or 't'. No other character is allowed."
		assert underscore + 1 == len(title) - 1, "The '_d' or '_t' pattern present in signal name must be the last part of the signal name."

def _verifyColumns(signals: List[str], timestamps: List[str], derivatives: List[str], colTitles: List[str]) -> None:
	# Verify all data is extracted
	assert len(signals) + len(timestamps) + len(derivatives) == len(colTitles), "Extracted column count does not match csv column count."
	# Verify we have the same amount of data points for each.
	assert len(timestamps) == len(signals), "Signal value and timestamp lists must have the same length."
	# Ensure all timestamps are found in the signals
	assert all([timestamp[:-2] in signals for timestamp in timestamps]), "Timestamp names, without '_t' must all be found in signal names."
	assert all([signal + '_t' in timestamps for signal in signals]), "Signal names, with '_t' suffix must all be found in timestamp names."
	# Ensure all derivatives 
	if len(derivatives) != 0:
		assert all([derivative[:-2] in signals for derivative in derivatives]), "Derivative names, without '_d' must all be found in signal names."
		assert all([signal + '_d' in derivatives for signal in signals]), "Signal names, with '_d' suffix must all be found in derivative names."
		assert len(derivatives) == len(signals), "If any derivatives are present, all derivatives must be present."
