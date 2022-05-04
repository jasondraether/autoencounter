from game import Game
from player import Player
from enemy import Enemy
import time

# Initialize empty board
width, height = 10, 10
g = Game(width, height, silence=True)
# This is bad practice but state dim is
# width of the board times the height of the board
# times the number of agents times the cell dimension
state_dim = width * height * 5 * 5
episodes = 500


# Define enemy and player positions
e1_c = (7,4)
e2_c = (7,5)
e3_c = (7,6)
p1_c = (2,2)
p2_c = (2,5)

# Initialize enemies and players
e1 = Enemy(
	state_dim=state_dim,
	amod=3,
	dmod=3,
	hp=15,
	ac=10,
	potions=1,
	ranged=False,
	n_agents=5,
	label='Enemy 1'
)
e2 = Enemy(
	state_dim=state_dim,
	amod=3,
	dmod=3,
	hp=15,
	ac=10,
	potions=1,
	ranged=False,
	n_agents=5,
	label='Enemy 2'
)
e3 = Enemy(
	state_dim=state_dim,
	amod=3,
	dmod=3,
	hp=15,
	ac=10,
	potions=1,
	ranged=False,
	n_agents=5,
	label='Enemy 3'
)
p1 = Player(
	strategy='random',
	amod=3,
	dmod=3,
	hp=20,
	ac=10,
	potions=1,
	ranged=False,
	n_agents=5,
	label='Player 1'
)
p2 = Player(
	strategy='random',
	amod=3,
	dmod=3,
	hp=20,
	ac=10,
	potions=1,
	ranged=False,
	n_agents=5,
	label='Player 2'
)

# Add entities to board
g.add(e1, *e1_c, label='E1')
g.add(e2, *e2_c, label='E2')
g.add(e3, *e3_c, label='E3')
g.add(p1, *p1_c, label='P1')
g.add(p2, *p2_c, label='P2')

episode_rewards = [{id(a): [] for a in [e1, e2, e3, p1, p2]} for _ in range(episodes)]
episode_means = [{id(a): 0 for a in [e1, e2, e3, p1, p2]} for _ in range(episodes)]
label_map = {id(a): a.label for a in [e1, e2, e3, p1, p2]}

for i in range(episodes):
	print(f'### Episode {i} ###', end='\r')
	# Game loop
	# Setup initial game and print to console
	state, agent = g.reset()
	#print(g)
	done = False
	while not done:
		# Get agent's action based on current state
		action = agent.get_action(state)
		# Take action on board, get next state and reward
		outcome_state, reward, done, next_state, next_agent = g.step(agent, action)
		# Update agent with info
		agent.update(state, action, outcome_state, reward, done)
		# Re-optimize agent
		agent.optimize()
		# Track rewards
		episode_rewards[i][id(agent)].append(reward)
		# Advance state
		state = next_state
		agent = next_agent
		# Print to console
		#print(g)

	for eid, rewards in episode_rewards[i].items():
		episode_means[i][eid] = sum(rewards)

for eid, total_reward in episode_means[0].items():
	print(f'{label_map[eid]} -> {total_reward}')

for eid, total_reward in episode_means[-1].items():
	print(f'{label_map[eid]} -> {total_reward}')
