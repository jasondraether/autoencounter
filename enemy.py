import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from entity import Entity
from model import DQN
from memory import Memory
import math

BATCH_SIZE = 32
MEMORY_SIZE = 1000
GAMMA = 0.999
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 200
UPDATE_COUNT = 100

class Enemy(Entity):
    def __init__(self, state_dim: int, *args, **kwargs):
        """Constructor for Enemy entitiy
        
        Args:
            state_dim (int): Vector size for input
            *args: Positional arguments for Entity constructor
            **kwargs: Keyword arguments f0r Entity constructor
        """
        super(Enemy, self).__init__(*args, **kwargs)
        self.state_dim = state_dim

        # Computes values for current state
        self.policy_net = DQN(self.state_dim, self.action_dim)
        self.optimizer = optim.RMSprop(self.policy_net.parameters())

        # Computes values for next state
        self.target_net = DQN(self.state_dim, self.action_dim)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        # Replay buffer
        self.replay = Memory(MEMORY_SIZE)
        # Number of optimizations done
        self.step_count = 0

        # Track rewards
        self.reward_sum = 0

    def update(self, state, action, outcome_state, reward, done):
        """Add new transition to replay buffer.

        Args:
            state (TYPE): Game state
            action (TYPE): Action taken by agent
            outcome_state (TYPE): Resulting state due to action
            reward (TYPE): Reward gained for taking that action at that state
        """

        self.replay.push((state, action, outcome_state, reward, done))

    def refresh(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.step_count = 0

    def get_action(self, state, greedy=False) -> int:
        """Get action according to policy.
        
        Args:
            state (TYPE): Game state
            greedy (bool, optional): Whether or not to take a greedy action
        
        Returns:
            int: Action
        """
        logits = self.policy_net.forward(torch.from_numpy(state.flatten().reshape(1, -1)).float()).detach().numpy()[0]
        if greedy:
            return np.argmax(logits)
        else:
            eps = EPS_END + (EPS_START - EPS_END) * math.exp(-1 * self.step_count / EPS_DECAY)
            avec = np.full(self.action_dim, eps/self.action_dim)
            avec[np.argmax(logits)] = 1 - eps + (eps/self.action_dim)
            return np.random.choice(self.action_dim, p=avec)

    def optimize(self):
        """Retrain models by sampling a batch from replay memory
        """
        if len(self.replay) < BATCH_SIZE:
            return

        self.step_count += 1

        # Sample from replay memory
        datum = self.replay.sample(BATCH_SIZE)

        # Unpack 
        state_batch = torch.Tensor(np.array([x[0] for x in datum]))
        action_batch = torch.LongTensor([x[1] for x in datum]).view(1, -1)
        next_state_batch = torch.Tensor(np.array([x[2] for x in datum]))
        reward_batch = torch.FloatTensor([x[3] for x in datum])
        done_batch = torch.BoolTensor([x[4] for x in datum])

        # Compute Q(s) and Q(s'), where Q(s') is greedy
        q_values = self.policy_net(state_batch).gather(1, action_batch)
        q_next_values = self.target_net(next_state_batch).max(1)[0].detach()

        # Compute target values
        expected_values = ((~done_batch)*q_next_values * GAMMA) + reward_batch

        # Compute Huber loss
        criterion = nn.SmoothL1Loss()
        loss = criterion(q_values, expected_values.view(1, -1))

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.policy_net.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()

        if self.step_count % UPDATE_COUNT == 0:
            self.refresh()
            