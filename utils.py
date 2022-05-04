import random

def roll(dice: int, n: int = 1) -> int:
	"""Roll a dice n times.
	
	Args:
	    dice (int): Sided die to roll (e.g. 6 for 6-sided, 20 for 20-sided)
	    n (int, optional): Number of times to roll the dice
	
	Returns:
	    int: Sum of the numbers rolled from the dicee
	"""
	return sum(random.randint(1, dice) for _ in range(n))