from collections import deque
import random

# From: https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
class Memory(object):
    def __init__(self, capacity: int):
        """Maintains a replay buffer with a specific capacity
        for the Q-learning algorithm.
        
        Args:
            capacity (int): Size of the replay buffer
        """
        self.memory = deque([], maxlen=capacity)

    def push(self, item):
        """Push an arbitrary sample into the replay buffer. If
        the memory queue is at capacity, the oldest sample
        is pushed out of the queue.
        
        Args:
            item (TYPE): Sample to be pushed into memory
        """
        self.memory.append(item)

    def sample(self, batch_size: int) -> list:
        """Randomly sample a number of items from the replay buffer
        without replacement.
        
        Args:
            batch_size (int): Number of items to sample
        
        Returns:
            list: Sampled items
        """
        return random.sample(self.memory, batch_size)

    def __len__(self) -> int:
        """Get number of items in replay buffer.
        
        Returns:
            int: Length of replay buffer
        """
        return len(self.memory)