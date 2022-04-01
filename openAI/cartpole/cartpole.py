import gym
import torch
import numpy as np
import os

gamma = 0.95
trainEpisodeCount = 250
testEpisodeCount = 10
stepCount = 10000
prefix = 'stlTool/openAI/cartpole'
modelSaveName = f'{prefix}/model.pickle'
saveTrainFile = f'{prefix}/data.py'


class MyNetwork(torch.nn.Module):

	def __init__(self):
		super().__init__()
		self.model = torch.nn.Sequential(
		    torch.nn.Linear(4, 16), torch.nn.ReLU(), torch.nn.Linear(16, 2)
		)
		for param in self.model.parameters():
			print(param.data)

	def forward(self, x):
		x = self.model(x)
		return torch.nn.functional.softmax(x, dim=1)


env = gym.make('CartPole-v1')
env.reset()
obsSpace = env.observation_space
actSpace = env.action_space

model = MyNetwork()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
eps = np.finfo(np.float32).eps.item()


def selectAction(model, state):
	state = torch.from_numpy(state).float().unsqueeze(0)
	probs = model(state)
	m = torch.distributions.Categorical(probs)
	action = m.sample()
	return action.item(), m.log_prob(action)


def selectActionBest(model, state):
	state = torch.from_numpy(state).float().unsqueeze(0)
	probs = model(state)
	if probs[0][0] > probs[0][1]:
		return 0, 0
	return 1, 0


def noop(*args, **kwargs):
	pass


def run(episodeCount, env, model, actionFn, training=True):
	rewards = []
	mode = 'w' if training else 'r'
	with open(saveTrainFile, mode) as f:
		if not training:
			f.write = noop
		f.write("trainingData = ([\n")
		for episodeIndex in range(episodeCount):
			state = env.reset()
			probs = []
			reward = 0
			f.write("\t[\n")
			for step in range(1, stepCount + 1):
				action, prob = actionFn(model, state)
				probs.append(prob)
				state, stepReward, done, note = env.step(action)
				f.write(f"\t\t({[x for x in state]}, {stepReward}, {done}, {note}),\n")
				reward += stepReward
				if done:
					break
			f.write(f"\t],\n")
			if training:
				loss = 0
				for i, prob in enumerate(probs):
					loss += -1 * (step-i) * prob
				optimizer.zero_grad()
				loss.backward()
				optimizer.step()
			if episodeIndex % 50 == 0 and training:
				print(f"Finished episode {episodeIndex}")
			rewards.append(reward)
		f.write("])\n")
	return rewards


if not os.path.exists(modelSaveName):
	print(f"No previously trained model found. Beginning training...")
	run(trainEpisodeCount, env, model, selectAction)
	print(f"Finished training!")
else:
	print(f"Found pre-existing model! Loading...")
	model = torch.load(modelSaveName)

print(f"Testing the model...")
rewards = run(testEpisodeCount, env, model, selectActionBest, training=False)

print(f"Model had the following scores in test: {rewards}")
if os.path.exists(modelSaveName):
	wantToDel = True if input("Do you want to delete this model's weights?\n") == 'y' else False
	if wantToDel:
		os.remove(modelSaveName)
if not os.path.exists(modelSaveName):
	wantToSave = True if input("Do you want to save the model weights?\n") == 'y' else False
	if wantToSave:
		print(f"Storing model weights...")
		torch.save(model, modelSaveName)

env.close()