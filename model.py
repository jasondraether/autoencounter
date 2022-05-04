import torch.nn as nn

class DQN(nn.Module):
    def __init__(self, input_dim: int, output_dim: int):
        """Deep Q-Network architecture. Input of the network
        is the state of the environment, and the output is
        the Q-value for taking each action at that state.
        
        Args:
            input_dim (int): Size of input
            output_dim (int): Size of output
        """
        super(DQN, self).__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim),
        )

    def forward(self, x):
        """Forward propogate input to the neural network. Input
        is flattened and passed in.
        
        Args:
            x (TYPE): Input of the neural network, which will be the state
        
        Returns:
            TYPE: Output logits representing the Q-value 
            for each action
        """
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits