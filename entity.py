from abc import ABC, abstractmethod
from typing import Union
import utils
import numpy as np
from memory import Memory

class Entity(ABC):
	def __init__(
		self, 
		amod: int, 
		dmod: int, 
		hp: int, 
		ac: int, 
		potions: int, 
		ranged: bool, 
		n_agents: int, 
		label: str = 'Entity'
	):
		"""A generic, simplified D&D entity. An entity has an
		attack modifier, a damage modifier, hit points, armor class,
		potions, and can be ranged or melee. An entity is also
		aware of the number of total entities in the game 
		(including itself). It also has a name to identify itself.
		
		Args:
		    amod (int): Attack modifier. Gets added to a 1d20 roll to see if the entity's attack hits
		    dmod (int): Damage modifier. Gets added to entities damage roll for extra damage.
		    hp (int): Hit points or "health" of the entity. This also sets the entity's max HP. Their
		    HP cannot exceed the max HP, and when their HP goes to zero (or below), the entity is dead.
		    Entities cannot be revived once they're dead.
		    ac (int): Armor class of the entity. If an attack roll meets or exceeds this number, the attack
		    lands, and the entity takes damage calculated from a damage roll.
		    potions (int): Number of potions the entity has in their inventory. Potions heal 2d4+2.
		    ranged (bool): Whether or not the entity is ranged. If an entity is ranged, it can attack
		    any other entity. If an entity is not ranged, it must be within one cell of another entity.
		    n_agents (int): Number of total entities (including self) in the game.
		    label (str, optional): Label of this entity.
		"""
		self.amod = amod 
		self.dmod = dmod
		self.hp = hp
		self.max_hp = hp
		self.ac = ac 
		self.potions = potions
		self.ranged = ranged
		self.n_agents = n_agents
		self.action_dim = 4 + 2*self.n_agents
		self.label = label
		self.alive = True

	def is_alive(self) -> bool:
		"""Check if agent is alive.
		
		Returns:
		    bool: True if agent is alive, otherwise False
		"""
		return self.alive

	def roll_attack(self) -> int:
		"""Roll attack to see if this entity's attack hits.
		
		Returns:
		    int: Attack score
		"""
		return utils.roll(20) + self.amod 

	def roll_damage(self) -> int:
		"""Roll damage to see the number of damage points to inflict in an attack.
		
		Returns:
		    int: Damage points
		"""
		return utils.roll(6, 2) + self.dmod

	def take_damage(self, points: int):
		"""Subtract hit points from this entity.
		
		Args:
		    points (int): Number of hit points to subtract
		"""
		self.hp -= points
		self.alive = self.hp > 0

	def heal(self, points: int):
		"""Heal this entity. If the entity is already dead,
		the entity is not healed. Entity cannot be healed beyond
		its max HP.
		
		Args:
		    points (int): Number of points to add to hit points
		"""
		if self.alive:
			self.hp = min(self.max_hp, self.hp + points)

	def use_potion(self) -> int:
		"""Use a potion and roll the number of health points
		to heal (this doesn't apply the heal to the entity). The number
		of potions is decreased by 1 if the entity has potions.
		If the entity has no potions, this returns 0. 
		
		Returns:
		    int: Number of points to heal
		"""
		if self.potions > 0:
			self.potions -= 1
			return utils.roll(4, 2) + 2
		return 0

	def optimize(self, *args, **kwargs):
		"""Optimize agent (used to retrain QNet for Enemies)
		"""
		pass 

	def update(self, *args, **kwargs):
		"""Update memory of agent (used for Enemies)
		"""
		pass

	@abstractmethod
	def get_action(self, state):
		"""Return an action vector.
		
		Args:
		    state (TYPE): Game state
		
		Returns:
		    TYPE: Action vector
		"""
		return None

	def __eq__(self, other):
		"""Test for equivalence between two entities. Two entities are equivalent
		if they literally are the same object
		
		Args:
		    other (TYPE): Other object to test for equivalence
		
		Returns:
		    TYPE: True if the unique IDs of both objects are the same, otherwise False
		"""
		return id(self) == id(other)

def ally(e1, e2):
	return type(e1) == type(e2)

def enemy(e1, e2):
	return not ally(e1, e2)