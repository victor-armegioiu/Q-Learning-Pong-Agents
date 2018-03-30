import os

LEFT = 0
RIGHT = 1

os.system('find . -type f -iname \*.png -delete')

strategies = [('random', 'random'), ('greedy', 'random'), ('greedy', 'greedy'), ('greedy', 'perfect'),
('e_greedy', 'random'), ('e_greedy', 'greedy'), ('e_greedy', 'perfect')]

test_strategies = [('greedy', 'perfect'), ['e_greedy', 'perfect']]

episodes = [100, 200, 250]
alphas = [0.6, 0.8, 1]
epss = [0.1, 0.05]
discounts = [0.3, 0.5, 0.6]

for strategy in test_strategies:
	for episode in episodes:
		for alpha in alphas:
			for eps in epss:
				if strategy[0] == 'greedy' and eps != 0.05:
					continue

				for discount in discounts:
					command = 'python3 pong.py '
					command += ' --left_player_strategy ' + strategy[LEFT]
					command += ' --right_player_strategy ' + strategy[RIGHT]
					command += ' --episodes ' + str(episode)
					command += ' --learning_rate ' + str(alpha)
					command += ' --epsilon ' + str(eps)
					command += ' --discount ' + str(discount)

					os.system(command)