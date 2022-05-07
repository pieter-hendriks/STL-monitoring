# pylint: disable-all
from cmath import exp
import torch.nn as nn
import torch
import numpy as np
import torch.functional as F
from torchsummary import summary
import random

# pylint: disable-all
import torch.nn as nn
import torch
import numpy as np
import torch.functional as F
from torchsummary import summary
import random


def createModel(kernelSize, inputLength):
	# In: 8x5 = 5 time series at a time? Not sure.
	# Kernel is a matrix, so we need <windowSize x kernelSize> input size, with kernel sliding over the window if window > kernel
	# window < kernel won't work

	model: nn.Sequential = nn.Sequential(
	    nn.Conv1d(kernelSize, 32, kernel_size=kernelSize, stride=1), nn.MaxPool1d(4), nn.Flatten(0, 1), nn.ReLU(),
	    nn.Linear(32 * (inputLength - kernelSize//2 - 5) // 4, 1)
	).double()
	# Keras spec
	#     nn.Conv1d(filters=64, kernel_size=5, activation='relu', input_shape=(80, 1)), nn.MaxPool1d(pool_size=2),
	#     F.Flatten(), nn.Dense(50, activation='relu'), nn.Dense(1)
	# )
	return model


def trainModel(model: nn.Sequential, inputLength: int, kernelSize: int, trainSize: int):
	# 50 lots of 5x80 input
	# [[[random.random() for _ in range(5)] for _ in range(80)] for _ in range(50)]
	inputs = np.random.randn(trainSize, kernelSize, inputLength)
	expectedResults = torch.from_numpy(np.amax(inputs, axis=(1, 2)))
	inputs = torch.from_numpy(inputs)

	optimizer = torch.optim.Adam(model.parameters())
	lossFn: torch.nn.MSELoss = torch.nn.MSELoss()
	for t in range(trainSize):
		data = inputs[t]
		optimizer.zero_grad()
		prediction = model(data)
		loss: torch.Tensor = lossFn(prediction, expectedResults[t])
		loss.backward()
		optimizer.step()

	#model.fit(inputs, expectedResults, epochs=1000, verbose=0)


def testModel(model: nn.Sequential, inputLength: int, kernelSize: int):
	totalScore = 0
	testInput = np.random.randn(10, kernelSize, inputLength)
	expectedResults = torch.from_numpy(np.amax(testInput, axis=(1, 2)))
	testInput = torch.from_numpy(testInput)
	for i in range(10):
		prediction = model(testInput[i])
		expected = expectedResults[i]
		print(f"Model predicted {prediction}, actual result {expected}")

		if prediction == expected:
			totalScore += 1
	print(f"Model scored {totalScore} out of 10 in the test run!")


if __name__ == "__main__":
	inputLength = 80
	kernelSize = 6
	trainSize = 25000
	model = createModel(kernelSize, inputLength)
	# summary(model, input_size=(8, 5))
	random.seed(1)  # Consistency
	trainModel(model, inputLength, kernelSize, trainSize)
	testModel(model, inputLength, kernelSize)