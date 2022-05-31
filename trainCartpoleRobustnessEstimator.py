# pylint: disable-all
import pickle
import dill
import torch
import os
from typing import Tuple, List
from stl.signals import Signal
from stl.utility import Interval
import matplotlib.pyplot as plt

# class MyNetwork(torch.nn.Module):
# 	def __init__(self):
# 		super().__init__()
# 		self.model = torch.nn.Sequential(
# 		    torch.nn.Linear(4, 32), torch.nn.ReLU(), torch.nn.Linear(32, 2)
# 		)

# 	def forward(self, x):
# 		x = self.model(x)
# 		return torch.nn.functional.softmax(x, dim=1)


class RobustnessEstimator(torch.nn.Module):

	def __init__(self):
		super().__init__()
		self.model = None
		self.optimizer = None

	def forward(self, x):
		return self.model(x)

	def train(self, dataSet):
		""" Expects pre-processed data set; tuples of input """
		...

	def test(self, dataSet):
		...

	def save(self, filename):
		with open(filename, "wb") as f:
			torch.save(self.model, f, pickle_protocol=pickle.HIGHEST_PROTOCOL)

	def load(self, filename):
		with open(filename, "rb") as f:
			self.model = torch.load(f)


def computeSampleSize(dataset, windowSize):
	count = 0
	for entry in dataset:
		signal: Signal = entry[0][0]
		lastTime = signal.computeLargestTimeBefore(signal.getTime(-1) - windowSize)
		count += signal.computeIndexForTime(lastTime) + 1
	return count

def MyNllLoss(dist: torch.distributions.Normal, target: float):
	return -dist.log_prob(target).sum()


class CartpoleRobustnessEstimator(torch.nn.Module):
	""" Estimator for the cart pole robustness. Requires that input length is >= 5. """

	def __init__(self):
		super().__init__()
<<<<<<< HEAD
		self.activation = torch.nn.LeakyReLU()
		self.lossFunction = torch.nn.L1Loss()
=======
		self.activation = torch.nn.Sigmoid()
		self.lossFunction = MyNllLoss
>>>>>>> 80fd398 (Windows changes for document work)
		self.model = torch.nn.Sequential(
		    torch.nn.AdaptiveAvgPool1d(35),  #
		    torch.nn.Conv1d(2, 2, 10),  #
		    self.activation,  #
<<<<<<< HEAD
		    torch.nn.Flatten(),  #
		    torch.nn.Linear(52, 32),  #
=======
		    torch.nn.Flatten(),  #
		    torch.nn.Linear(52, 128),  #
>>>>>>> 80fd398 (Windows changes for document work)
		    self.activation,  #
		    torch.nn.Linear(32, 16),  #
		    self.activation,  #
		    torch.nn.Linear(16, 2)
		).cuda()
		self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-3)

	def forward(self, x):
		out = self.model(x)
		mean = out[..., 0][..., None]
		std = torch.clamp(out[..., 1][..., None], min=0.01)
		dist = torch.distributions.Normal(mean, std)
		return dist

	def train(self, dataSet):
		"""
		Trains the model on the entirety of the given data set.
		Expected format: List[Tuple(Tuple[Signal, Signal], Signal)]
		"""
		dataIndex = 0
		losses = []
		for entry in dataSet:
			prediction = self.forward(entry[0])
			self.optimizer.zero_grad()
			loss = self.lossFunction(prediction, entry[1].squeeze())
			losses.append(loss.item())
			loss.backward()
			self.optimizer.step()
			dataIndex += 1
			if dataIndex % 5000 == 0:
				print(f"Handled {dataIndex} out of {len(dataSet)} samples")
		plt.plot(losses, label="losses")
		plt.show()
		print(f"Handled all samples: {dataIndex-1} out of {len(dataSet)}")

	def test(self, dataSet):
		"""
		Tests the model. Prints performance stats.
		"""
		outputs: List[torch.distributions.Normal, float] = []
		dataIndex = 0
		for entry in dataSet:
			prediction = self.forward(entry[0])
			outputs.append((prediction, entry[1].item()))
			dataIndex += 1
			if dataIndex % 5000 == 0:
				print(f"Handled {dataIndex} out of {len(dataSet)} samples")
		print(f"Handled all samples: {dataIndex-1} out of {len(dataSet)}")

		#plt.plot([x[0] for x in outputs], label="estimated", color='blue')
		times = list(range(len(outputs)))
		print(type(times))
		print(times)
		plt.plot(times, [x[1] for x in outputs], label="expected", color='red')
		y1 = [(x[0].mean + x[0].stddev).item() for x in outputs]
		y2 = [(x[0].mean - x[0].stddev).item() for x in outputs]
		print(times)
		print(y1)
		print(y2)
		plt.fill_between(times, y1, y2, color='blue', alpha=0.5, label="estimated")
		plt.legend()
		plt.show()


def preprocess(dataset, windowSize):
	""" Expected data in-format List[Tuple(Tuple[Signal, Signal], Signal)]
	out-format: List[Tensor[values, values], Tensor[labelvalues]]"""
	# This behaviour is cartpole specific, since the data sets differ between environments.
	entry: Tuple[Tuple[Signal, Signal], Signal]
	for entry in dataset:
		pSignal = entry[0][0]
		cSignal = entry[0][1]
		labels = entry[1]
		# if pSignal.getTimes() != cSignal.getTimes():
		# 	pSignal, cSignal = Signal.computeCheckpointsForComparableSignal(pSignal, cSignal)
		i = 0
		# pSignal and cSignal now have matching timestamps
		while pSignal.getTime(-1) >= pSignal.getTime(i) + windowSize:  # Also applies to cSignal
			interval = Interval(pSignal.getTime(i), pSignal.getTime(i) + windowSize)
			pIn = pSignal.computeInterval(interval)
			cIn = cSignal.computeInterval(interval)
			inTensor = torch.tensor([[pIn.getValues(), cIn.getValues()]]).cuda()
			outTensor = torch.tensor(labels.computeInterpolatedValue(pSignal.getTime(i))).cuda()
			yield (inTensor, outTensor)
			i += 1


# print("Cartpole data import is enabled!")
# from examples.cartpole.data_converted import data

# trainData = data[:-10]
# testData = data[-10:]

# print("Start train convert")
# trainData = list(preprocess(trainData, 50))
# print("Start test convert")
# testData = list(preprocess(testData, 50))
# with open("traindata.pickle", "wb") as f:
# 	print("Start train write")
# 	torch.save(trainData, f, pickle_module=dill, pickle_protocol=pickle.HIGHEST_PROTOCOL)
# with open("testdata.pickle", "wb") as f:
# 	print("Start test write")
# 	torch.save(testData, f, pickle_module=dill, pickle_protocol=pickle.HIGHEST_PROTOCOL)
# print("Finished converting data!")
# exit(1)

saveFileName = "estimator.pickle"
skipTraining = False

if os.path.exists(saveFileName):
	ans = input("Save file exists. Use it?\n")
	if ans.lower() in ('yes', 'y'):
		skipTraining = True
if skipTraining:
	with open(saveFileName, 'rb') as f:
		estimator = torch.load(f)
	for name, param in estimator.model.named_parameters():
		if param.requires_grad:
			print(name, param.data)
else:
	estimatorPoolSize = 25
	print("Loading the train data!")
	with open("traindata.pickle", "rb") as f:
		trainData = torch.load(f, pickle_module=dill, map_location='cuda:0')
	print("Train data loaded...")

	estimator = CartpoleRobustnessEstimator()
	estimator.train(trainData)
	with open(saveFileName, 'wb') as f:
		torch.save(estimator, f, pickle_protocol=pickle.HIGHEST_PROTOCOL)
print("Loading the test data!")
with open("testdata.pickle", "rb") as f:
	testData = torch.load(f, pickle_module=dill, map_location='cuda:0')
print("Test data loaded...")
estimator.test(testData)

# Import cartpole converted dataset
# Call estimator.train(dataset)
# Generate random data
# Test the estimator
# (Or, probably better, exclude some data from train set and use that to test)
