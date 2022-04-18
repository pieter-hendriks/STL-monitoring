import gym
import torch
import numpy as np
import os


gamma = 0.95
trainEpisodeCount = 500
testEpisodeCount = 10
stepCount = 500
modelSaveName = 'model.pickle'
class MyNetwork(torch.nn.Module):
	def __init__(self):
		super().__init__()
		self.flatten = torch.nn.Flatten()
		self.model = torch.nn.Sequential(
			torch.nn.Linear(4, 8),
			torch.nn.ReLU(),
			torch.nn.Linear(8, 2)
		)
	
	def forward(self, x):
		x = self.model(x)
		return torch.nn.functional.softmax(x, dim=1)



env = gym.make('CartPole-v1')
env.reset()
obsSpace = env.observation_space
actSpace = env.action_space

device = 'cuda' if torch.cuda.is_available() else 'cpu'

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


def run(episodeCount, env, model, actionFn, training=True):
	rewards = []
	for episodeIndex in range(episodeCount):
		state = env.reset()
		probs = []
		reward = 0
		for step in range(1, stepCount + 1):
			action, prob = actionFn(model, state)
			probs.append(prob)
			state, stepReward, done, note = env.step(action)
			reward += stepReward
			if done: 
				break
		if training:
			loss = 0
			for i, prob in enumerate(probs):
				loss += -1 * (step - i) * prob
			optimizer.zero_grad()
			loss.backward()
			optimizer.step()
		print(f"Finished episode {episodeIndex}")
		rewards.append(reward)
	return rewards

if not os.path.exists(modelSaveName):
	print(f"No previously trained model found. Beginning training...")
	run(trainEpisodeCount, env, model, selectAction)
	print(f"Finished training! Storing model weights...")
	torch.save(model, modelSaveName)
else:
	print(f"Found pre-existing model! Loading...")
	model = torch.load(modelSaveName)


print(f"Testing the model...")
rewards = run(testEpisodeCount, env, model, selectActionBest, training=False)

print(f"Model had the following scores in test: {rewards}")

env.close()