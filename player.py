from entity import Entity
import numpy as np
import random

# Valid keyboard inputs from user
VALID_INPUTS = ['w', 'a', 's', 'd', 'q', 'e']

class Player(Entity):
	def __init__(self, strategy: str = 'manual', *args, **kwargs):
		"""Constructor for Player entity along with a strategy.
		
		Args:
		    strategy (str, optional): Strategy type to use. One of ['manual', 'random', 'nearest', 'flee']
		    *args: Positional arguments for Entity constructor
		    **kwargs: Keyword arguments f0r Entity constructor
		"""
		super(Player, self).__init__(*args, **kwargs)
		self.strategy = strategy

	def get_action(self, state) -> int:
		"""Get an action according to this player's given strategy. 'state' is unused.
		
		Args:
		    state (TYPE): Game state
		
		Returns:
		    int: Action
		"""
		if self.strategy == 'manual':
			return self.get_manual_action()
		elif self.strategy == 'random':
			return self.get_random_action()
		elif self.strategy == 'nearest':
			return self.get_nearest_action()
		elif self.strategy == 'flee':
			return self.get_flee_action()

		return None

	def get_flee_action(self):
		"""Run away from the nearest enemy
		"""
		pass

	def get_nearest_action(self):
		"""Attack the nearest enemy
		"""
		pass

	def get_random_action(self) -> int:
		"""Take random action
		
		Returns:
		    int: Action
		"""
		return random.randint(0, self.action_dim-1)

	def get_manual_action(self) -> int:
		"""Get an action from manual keyboard input.
		
		Returns:
		    int: Action
		"""
		# Show initial prompt
		print(f'({self.label}) HP: {self.hp} | Potions: {self.potions}')
		ain = input(f'(wasd) Move | (q) Attack | (e) Heal: ').lower()
		valid = ain in VALID_INPUTS
		# Repeat until input is valid
		while not valid:
			ain = input(f"Input {ain} invalid. Valid inputs are [{''.join(VALID_INPUTS)}]. \nTry again: ").lower()
			valid = ain in VALID_INPUTS
		# Construct action vector
		action = None
		if ain == 'w': # Move up
			action = self.action_dim-1
		elif ain == 's': # Move down
			action = self.action_dim-2
		elif ain == 'a': # Move left
			action = self.action_dim-3
		elif ain == 'd': # Move right
			action = self.action_dim-4
		elif ain == 'q': # Attack
			target = int(input(f'Which entity to attack? [0-{self.n_agents-1}]: '))
			valid = target >= 0 and target < self.n_agents
			# Repeat until input is valid
			while not valid:
				target = int(input(f'Input {target} invalid.\nWhich entity to attack? [0-{self.n_agents-1}]: ')) 
				valid = target >= 0 and target < self.n_agents
			action = target
		elif ain == 'e': # Heal
			target = int(input(f'Which entity to heal? [0-{self.n_agents-1}]: '))
			valid = target >= 0 and target < self.n_agents
			# Repeat until input is valid
			while not valid:
				target = int(input(f'Input {target} invalid.\nWhich entity to heal? [0-{self.n_agents-1}]: ')) 
				valid = target >= 0 and target < self.n_agents
			action = self.n_agents + target
		else: # Unrecognized
			action = None
			
		return action