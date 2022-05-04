import numpy as np 
from typing import Tuple

class Board(object):
	def __init__(self, rows: int, cols: int):
		"""Board maintains a game board which marks cells on
		the board as free or used. A cell can only be occupied by
		one entity which is tracked by its object ID or "eid". The
		board is represented internally with a 2D array, with the
		top left coordinate being (0, 0). Rows are the first
		coordinate, columns are the second coordinate.
		
		Args:
		    rows (int): Number of rows in board
		    cols (int): Number of columns in board
		"""
		self.grid = np.full((rows, cols), False) # False if empty, True if filled
		self.rows = rows 
		self.cols = cols
		self.ents = {} # (row, col) -> eid
		self.loc = {} # eid -> (row, col)

	def free(self, x: int, y: int) -> bool:
		"""Check if a cell on the board is unoccupied.
		
		Args:
		    x (int): Row on the board
		    y (int): Column on the board
		
		Returns:
		    bool: True if the cell is unoccupied, False otherwise.
		"""
		assert self.inbounds(x, y)
		return not(self.grid[x, y])

	def used(self, x: int, y: int) -> bool:
		"""Check if a cell on the board is occupied.
		
		Args:
		    x (int): Row on the board
		    y (int): Column on the board
		
		Returns:
		    bool: True if the cell is occupied, False otherwise.
		"""
		assert self.inbounds(x, y)
		return not(self.free(x, y))

	def add(self, eid: int, x: int, y: int):
		"""Add an entity to an unoccupied cell.
		
		Args:
		    eid (int): Unique ID representing the entity/object
		    x (int): Row on the board
		    y (int): Column on the board
		"""
		assert self.free(x, y)
		assert self.inbounds(x, y)
		self.grid[x, y] = True
		self.ents[(x, y)] = eid
		self.loc[eid] = (x, y)

	def remove(self, eid: int):
		"""Remove an entity from its occupied cell.
		
		Args:
		    eid (int): Unique ID to lookup the entity location
		"""
		assert eid in self.loc
		x, y = self.query(eid)
		self.grid[x, y] = False
		del self.ents[(x, y)]
		del self.loc[eid]

	def inbounds(self, x: int, y: int) -> bool:
		"""Check if two coordinates are within the boundaries of the board.
		
		Args:
		    x (int): Row on the board
		    y (int): Column on the board
		
		Returns:
		    bool: True if the coordinates are inbounds, otherwise False
		"""
		return (x >= 0) and (x < self.rows) and (y >= 0) and (y < self.cols)

	def move(self, x: int, y: int, xf: int, yf: int):
		"""Move an entity from (x, y) to (xf, yf). The entity
		must exist on the board at (x, y) already, and (xf, yf)
		must be a free space on the board, and both coordinates
		must be valid, inbound coordinates.
		
		Args:
		    x (int): Row on the board of the entity
		    y (int): Column on the board of the entity
		    xf (int): Target row on the board for the entity to move to
		    yf (int): Target column on the board for the entity to move to
		"""
		assert self.inbounds(x, y)
		assert self.inbounds(xf, yf)
		assert (x, y) in self.ents
		assert self.used(x, y)
		assert self.free(xf, yf) 
		self.grid[x, y] = False 
		self.grid[xf, yf] = True
		eid = self.ents[(x, y)]
		del self.ents[(x, y)]
		del self.loc[eid]
		self.ents[(xf, yf)] = eid
		self.loc[eid] = (xf, yf)

	def query(self, eid: int) -> Tuple[int, int]:
		"""Lookup an entity by ID on the board and return 
		the row and column that it occupies.
		
		Args:
		    eid (int): Unique ID to lookup the entity location
		
		Returns:
		    tuple[int, int]: Row and column coordinates of the entity
		"""
		assert eid in self.loc
		return self.loc[eid]

	def lquery(self, x: int, y: int) -> int:
		"""Lookup an entity by location on the board and return 
		the entity ID
		
		Args:
		    x (int): Row on the board of the entity
		    y (int): Column on the board of the entity
		
		Returns:
		    int: Unique ID of the entity
		"""
		assert (x, y) in self.ents
		return self.ents[(x, y)]

	def belongs(self, eid: int) -> bool:
		"""Check if an entity exists on the board
		
		Args:
		    eid (int): Unique ID to lookup the entity
		
		Returns:
		    bool: True if the entity exists on the board, otherwise False
		"""
		return eid in self.loc

	def near(self, eid1: int, eid2: int) -> bool:
		"""Check if two entities are within one cell of each other. If
		the entities are the same, and the entities are on the board,
		this also returns True.
		
		Args:
		    eid1 (int): Unique ID to lookup the first entity's location
		    eid2 (int): Unique ID to lookup the second entity's location. Doesn't have to be on the board.
		
		Returns:
		    bool: True if the entities are within one cell of each other OR
		    the entities are the same, otherwise False.
		"""
		assert eid1 in self.loc 

		if eid2 not in self.loc:
			return False

		if eid1 == eid2:
			return True

		x1, y1 = self.query(eid1)
		x2, y2 = self.query(eid2)

		return (x1 + 1 == x2 and y1 == y2) or \
			   (x1 - 1 == x2 and y1 == y2) or \
			   (x1 == x2 and y1 + 1 == y2) or \
			   (x1 == x2 and y1 - 1 == y2)

	def __str__(self) -> str:
		"""String overload for Board. Returns string representation
		of grid, which is a NumPy array.
		
		Returns:
		    str: String representing the board grid
		"""
		return str(self.grid)
