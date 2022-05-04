import numpy as np
from enemy import Enemy
from player import Player
from entity import ally
from board import Board
from typing import Union
import random
import utils

class Game(object):
	def __init__(self, rows: int, cols: int, silence: bool = False):
		"""Constructor for Game. Game handles the logic behind D&D and 
		a combat encounter between players and enemies. The Game maintains a Board
		object, of which the top left corner is referenced as (row=0, col=0). Moving
		up decreases the row index, moving left decreases the column index. Any entities
		(Players or Enemies) are referred to as "agents" in this code.
		
		Args:
		    rows (int): Number of rows in board
		    cols (int): Number of columns in board
		    silence (bool, optional): Whether or not to print out actions
		"""
		self.silence = silence
		self.board = Board(rows, cols)
		self.rows = rows
		self.cols = cols
		# id(agent) -> agent
		self.agents = {}
		# Initiative order of agents
		self.order = []
		# Original starting position of agents
		self.initial_position = {}
		# id(agent) -> unique index of agent
		self.agent_index = {}
		# unique index of agent -> id(agent)
		self.index_to_agent = {}
		# Number of agents in the game (count of players and enemies)
		self.n_agents = 0
		# Number of possible sparse values for a single agent for a single cell
		# These are [self, melee ally, ranged ally, melee enemy, ranged enemy]
		self.cell_dim = 5
		# id(agent) -> label
		self.label_map = {}
		# Track agents whose HP was brought down to zero
		self.dead = set()

	def initiative(self):
		"""Generate a turn order by randomly shuffling the list of agents
		"""
		agent_list = list(self.agents.values())
		random.shuffle(agent_list)
		self.order = agent_list

	def add(self, agent: Union[Player, Enemy], x: int, y: int, label: str = ''):
		"""
		Add an agent to the board at the location x, y, and give a board
		label. Store its initial position, its board label, and its agent index.
		
		Args:
		    agent (Union[Player, Enemy]): Description
		    x (int): Description
		    y (int): Description
		    label (str, optional): Description
		"""
		assert len(label) == 2
		eid = id(agent)
		assert eid not in self.agents
		self.board.add(eid, x, y)
		self.agents[eid] = agent
		self.initial_position[eid] = (x, y)
		self.label_map[eid] = label
		self.agent_index[eid] = self.n_agents
		self.index_to_agent[self.n_agents] = agent
		self.n_agents += 1

	def pop(self):
		"""Retrieve the agent at the top of the initiative
		order, add it to the back, and return the agent.
		
		Returns:
		    TYPE: Agent at the top of the initiative
		"""
		assert len(self.order) > 0
		agent = self.order.pop(0)
		self.order.append(agent)
		return agent

	def step(self, agent: Union[Player, Enemy], action: int):
		"""
		Allow an agent to take an action in the game. The steps are as follows:
		    	1. Apply the action to the current board
		    	2. Get the outcome of the state with the perspective of the current agent
		    	3. Get the reward of that action
		    	4. Get the new agent from initiative order and update the order
		    	5. Regenerate the state from the perspective of the new agent
		
		Note that self.board is the ONLY thing we modify internally to track 
		the state change, as well as the agents themselves.
		
		Args:
		    agent (Union[Player, Enemy]): Agent who is applying the action
		    action (int): Action
		
		Returns:
		    TYPE: a tuple containing the outcome state from the perspective of the
		    current agent, the reward from the action taken, whether that action 
		    led to completion, the next state from the perspective of the next agent,
		    and the next agent in the initiative order (modifies the order)
		"""
		# Take action of current agent and get outcome
		outcome_state, reward = self.apply_action(agent, action)

		# Check if remaining entitites are all allies
		done = all(ally(x, y) for x in self.order for y in self.order)

		# See who is at the head of the queue
		next_agent = self.pop()

		# Generate next state from perspective of next agent
		next_state = self.generate_state(next_agent)
		return outcome_state, reward, done, next_state, next_agent

	def handle_attack(self, agent: Union[Player, Enemy], action: int):
		target = self.index_to_agent[action]

		if not self.silence: print(f'Action: {self.label_map[id(agent)]} attacking {self.label_map[id(target)]}')

		hit = agent.roll_attack() >= target.ac
		reachable = agent.ranged or self.board.near(id(agent), id(target))
		damage = agent.roll_damage()
		is_self = id(target) == id(agent)
		is_ally = ally(agent, target)
		is_enemy = not ally(agent, target)

		# This shouldn't happen, but attacking an already dead target
		if id(target) in self.dead:
			reward = -1
			if not self.silence: print('Target is already dead.')
		# Not possible to reach target
		elif not reachable:
			reward = -1
			if not self.silence: print('Cannnot be reached.')
		# Target is reachable
		else:
			# Successfully hit target
			if hit:
				# Deal damage to target
				target.take_damage(damage)
				if is_self:
					reward = -2*damage # Really bad to harm ourselves
				elif is_ally:
					reward = -damage # Bad to harm an ally
				elif is_enemy:
					reward = damage # Good to harm an enemy
				if not self.silence: print(f'Hit target for {damage} damage.')
				if not target.is_alive(): # If target is dead, boost the award
					reward *= 2
					if not self.silence: print('Killed target.')
					# Add the target to the dead counter, remove from initiative and board
					self.dead.add(id(target))
					self.order.remove(target)
					self.board.remove(id(target))
			# Missed the target
			else:
				if not self.silence: print('Missed target.')
				reward = -1
		return reward

	def handle_heal(self, agent: Union[Player, Enemy], action: int):
		target = self.index_to_agent[action]

		if not self.silence: print(f'Action: {self.label_map[id(agent)]} healing {self.label_map[id(target)]}')

		reachable = self.board.near(id(agent), id(target))
		points = agent.use_potion()
		is_self = id(target) == id(agent)
		is_ally = ally(agent, target)
		is_enemy = not ally(agent, target)

		# Agent doesn't have any potions
		if points == 0: 
			reward = -1
			if not self.silence: print('Out of potions.')
		# Target is dead and can't be healed
		elif not target.is_alive():
			reward = -1 
			if not self.silence: print('Target is already dead.')
		# Target is not reachable, we wasted a potion
		elif not reachable:
			reward = -1
			if not self.silence: print('Cannnot be reached.')
		# Target is reachable, alive, and we have potions
		else:
			# Healing ourself
			if is_self:
				reward = points
			# Healing an ally
			elif is_ally:
				reward = points
			# Heaeling an enemy
			elif is_enemy:
				reward = -points # Bad to heal an enemy
			if not self.silence: print(f'Healed target for {points} points.')
			target.heal(points)
		return reward

	def handle_up(self, agent: Union[Player, Enemy]):
		if not self.silence: print(f'Action: {self.label_map[id(agent)]} moving up.')

		x, y = self.board.query(id(agent))
		xf, yf = x - 1, y
		if self.board.inbounds(xf, yf) and self.board.free(xf, yf):
			reward = 0
			self.board.move(x, y, xf, yf)
		# Out of bounds or collision!
		else: 
			reward = -1
		return reward

	def handle_down(self, agent: Union[Player, Enemy]):
		if not self.silence: print(f'Action: {self.label_map[id(agent)]} moving down.')

		x, y = self.board.query(id(agent))
		xf, yf = x + 1, y
		if self.board.inbounds(xf, yf) and self.board.free(xf, yf):
			reward = 0
			self.board.move(x, y, xf, yf)
		# Out of bounds or collision!
		else: 
			reward = -1
		return reward

	def handle_left(self, agent: Union[Player, Enemy]):
		if not self.silence: print(f'Action: {self.label_map[id(agent)]} moving left.')

		x, y = self.board.query(id(agent))
		xf, yf = x, y - 1
		if self.board.inbounds(xf, yf) and self.board.free(xf, yf):
			reward = 0
			self.board.move(x, y, xf, yf)
		# Out of bounds or collision!
		else: 
			reward = -1 
		return reward

	def handle_right(self, agent: Union[Player, Enemy]):
		if not self.silence: print(f'Action: {self.label_map[id(agent)]} moving right.')

		x, y = self.board.query(id(agent))
		xf, yf = x, y + 1
		if self.board.inbounds(xf, yf) and self.board.free(xf, yf):
			reward = 0
			self.board.move(x, y, xf, yf)
		# Out of bounds or collision!
		else: 
			reward = -1
		return reward


	def apply_action(self, agent: Union[Player, Enemy], action: int):
		"""Apply the action from the agent to the board, modifying the board
		state. Return the new state of the board from the perspective of
		the agent who took the action. Actions are:
		[0 - n_agents-1] -- Attack another agent (according to agent index)
		[n_agents - 2*n_agents-1] -- Heal another agent (according to agent index)
		2*n_agents -- Move up
		2*n_agents+1 -- Move down
		2*n_agents+2 -- Move left
		2*n_agents+3 -- Move right
		
		Args:
		    agent (Union[Player, Enemy]): Agent taking the action
		    action (int): Action
		
		Returns:
		    TYPE: Resulting state from the agent's action
		
		Raises:
		    ValueError: Raises error upon receiving invalid action
		"""

		# Attacking another agent
		if action >= 0 and action < self.n_agents:
			reward = self.handle_attack(agent, action)
		# Healing another agent
		elif action >= self.n_agents and action < 2*self.n_agents:
			reward = self.handle_heal(agent, action - self.n_agents)
		# Moving up
		elif action == 2*self.n_agents:
			reward = self.handle_up(agent)
		# Moving down
		elif action == 2*self.n_agents + 1:
			reward = self.handle_down(agent)
		# Moving left
		elif action == 2*self.n_agents + 2:
			reward = self.handle_left(agent)
		# Moving right
		elif action == 2*self.n_agents + 3:
			reward = self.handle_right(agent)
		# Error
		else:
			print(action)
			raise ValueError(f'Action {action} out of bounds.')

		outcome_state = self.generate_state(agent)
		return outcome_state, reward
		 
	def generate_state(self, current_agent: Union[Player, Enemy]):
		"""Generate the state of the board from the perspective of the current_agent. For a given
		cell, we can have [self, melee ally, ranged ally, melee enemy, ranged enemy] for
		each agent as a sparse vector. A empty cell has zero'd vectors for all agents.
		An occupied cell will only have one of these sparse vectors according to the
		agent who occupies that cell. If an agent is dead, they don't occupy
		any cells.
		
		Args:
		    current_agent (Union[Player, Enemy]): Agent whose perspective is used
		    to generate the state
		
		Returns:
		    TYPE: Game state
		
		Raises:
		    ValueError: Throws an error if we have an agent in the order who
		    isn't recognized
		"""
		state = np.zeros((self.rows, self.cols, self.n_agents, self.cell_dim)) 
		current_eid = id(current_agent)

		# Build state vector based on each agent
		for agent in self.order:
			eid = id(agent)
			x, y = self.board.query(eid)
			index = self.agent_index[eid]
			# Self
			if eid == current_eid:
				state[x, y, index, 0] = 1
			# Melee ally
			elif agent.ranged == False and ally(agent, current_agent): 
				state[x, y, index, 1] = 1
			# Ranged ally
			elif agent.ranged and ally(agent, current_agent): 
				state[x, y, index, 2] = 1
			# Melee enemy
			elif agent.ranged == False and not ally(agent, current_agent): 
				state[x, y, index, 3] = 1
			# Ranged enemy
			elif agent.ranged and not ally(agent, current_agent): 
				state[x, y, index, 4] = 1
			# Error
			else:
				raise ValueError(f'Unrecognized agent type.')

		return state

	def reset(self):
		"""Reset the state of the game back to its original
		state with the agents in their initial positions.
		
		Returns:
		    TYPE: A tuple of the starting state and the agent who is 
		    first in the new initiative order
		"""
		self.initiative()
		self.board = Board(self.rows, self.cols)
		self.dead = set()
		for eid, (x, y) in self.initial_position.items():
			self.board.add(eid, x, y)
		starting_agent = self.pop()
		state = self.generate_state(starting_agent)
		return state, starting_agent

	def __str__(self):
		"""Pretty-print the state of the board with each
		agents board label
		
		Returns:
		    TYPE: Formatted string for board
		"""
		output_str = ''
		for i in range(self.rows):
			for j in range(self.cols):
				# Empty space
				if self.board.free(i, j):
					output_str += '__ '
				else:
					# Entity space
					eid = self.board.lquery(i, j)
					output_str += self.label_map[eid] + ' '
			output_str += '\n\n'
		# Show a map below of each agents board label and index (for attacking and healing)
		for eid, eindex in sorted(self.agent_index.items(), key=lambda x: x[1]):
			output_str += f'{eindex}: {self.label_map[eid]}\n'

		return output_str


