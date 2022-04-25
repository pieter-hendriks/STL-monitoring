from stl.signals import Signal
import random

values = []
for i in range(10000):
	values.append(random.random())

times = list(range(10000))
signal: Signal = Signal('ritam', times, values)
