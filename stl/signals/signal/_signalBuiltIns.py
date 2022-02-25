def __str__(self) -> str:
	ret = ["Signal with the following checkpoint entries: "]
	for cp in self.checkpoints:
		ret.append(f'\t{cp.getTime()} -> <{cp.getValue()}, {cp.getDerivative()}>')
	return '\n'.join(ret)

def __repr__(self) -> str:
	times, values, derivatives = [],[],[]
	for x in self.checkpoints:
		times.append(x.getTime())
		values.append(x.getValue())
		derivatives.append(x.getDerivative())
	return f"Signal('{self.name}', {times.__repr__()}, {values.__repr__()}, {derivatives.__repr__()})"

def __eq__(self, other: 'Signal') -> bool: # type: ignore
	""" Check equality with other Signals. """
	if type(self) != type(other):
		return False
	if self.name != other.name:
		return False
	if len(self.checkpoints) != len(other.checkpoints):
		return False
	for scp, ocp in zip(self.checkpoints, other.checkpoints):
		if scp != ocp:
			return False
	return True