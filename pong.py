__author__ = 'Victor Armegioiu'

import os, time, random, sys
from termcolor import cprint 
from pyfiglet import figlet_format
from math import ceil
from copy import deepcopy
from argparse import ArgumentParser
from matplotlib import pyplot as plt

bottom_left, bottom_right = "┗", "┛"
top_left, top_right = "┏", "┓"

WIDTH, HEIGHT = 31, 21 // 3
INF = int(1e15)

LEFT = 0
RIGHT = 1
ENDING_SCORE = -1

class Paddle:
	def __init__(self, col, line, top_size, bottom_size):
		self.col = col
		self.line = line
		self.top_size = top_size
		self.bottom_size = bottom_size

	def covers_line(self, line_idx):
		return line_idx == self.line or self.line + self.bottom_size >= line_idx >= self.line\
		or self.line - self.top_size <= line_idx <= self.line

	def available_actions(self):
		actions = [0]
		if self.line + self.bottom_size + 1 <= HEIGHT:
			actions.append(1)

		if self.line - self.top_size - 1 >= 1:
			actions.append(-1)

		return tuple(actions)

	def move(self, action):
		self.line += action


def draw_line(ball_pos, line_idx, paddles):
	line = list("┃" + WIDTH * " " + "┃")

	if ball_pos[0] == line_idx:
		line[ball_pos[1]] = "•"

	for paddle in paddles:
		if paddle.covers_line(line_idx):
			line[paddle.col] = "┃"

	print("".join(line))


def update_ball_state(ball_pos, ball_dir, paddles):
	scores = [0, 0]

	if ball_pos[0] == 1 or ball_pos[0] == HEIGHT:
		ball_dir[0] *= -1

	if ball_pos[1] == 1 or ball_pos[1] == WIDTH:
		ball_dir[1] *= -1
		scores = [0, -1] if ball_pos[1] == WIDTH else [-1, 0]

	if ball_pos[1] == 2 and paddles[0].covers_line(ball_pos[0]):
		ball_dir[1] *= -1
		scores = [1, 0]
		
	if ball_pos[1] == WIDTH - 1 and paddles[1].covers_line(ball_pos[0]):
		ball_dir[1] *= -1
		scores = [0, 1]

	ball_pos[0] += ball_dir[0]
	ball_pos[1] += ball_dir[1]

	return (scores, ball_pos, ball_dir)	


def reset_game(strategy):
	ball_pos = [random.randint(2, HEIGHT - 1), ceil(WIDTH / 2)]
	ball_dir = [random.choice([-1, 1]), random.choice([-1, 1])]

	left_paddle = Paddle(1, ceil(HEIGHT / 2), 0, 0) 
	right_paddle = Paddle(WIDTH, ceil(HEIGHT / 2), HEIGHT // 2 if strategy[RIGHT] == 'perfect' else 0 ,
												 HEIGHT // 2 if strategy[RIGHT] == 'perfect' else 0)

	return ball_pos, ball_dir, left_paddle, right_paddle


def epsilon_greedy(Q, seen_combinations, state, legal_actions, epsilon):
    not_tried_yet = []
    for action in legal_actions:
        if (state, action) not in seen_combinations:
            not_tried_yet.append(action)

    if not_tried_yet != []:
        return random.choice(not_tried_yet)

    if random.random() < epsilon:
        return random.choice(legal_actions)
    else:
        return best_action(Q, state, legal_actions)


def best_action(Q, state, legal_actions):
    best_action = None
    best_action_utility = -INF

    for action in legal_actions:
        if (state, action) not in Q:
            Q[state, action] = 0

        if Q[state, action] > best_action_utility:
            best_action_utility = Q[state, action]
            best_action = action

    return best_action


def get_action(player, player_strategy, Q, seen_combinations, state, actions, epsilon):
	action = 0
	if player_strategy[player] == 'e_greedy':
		action = epsilon_greedy(Q, seen_combinations, state, actions, epsilon)

	elif player_strategy[player] == 'greedy':
		action = epsilon_greedy(Q, seen_combinations, state, actions, 0)

	elif player_strategy[player] == 'random':
		action = random.choice(actions)

	elif player_strategy[player] == 'perfect':
		action = 0

	return action
	

def q_learning(args):
	Q = {}

	left_player_combinations = {}
	right_player_combinations = {}

	epsilon, alpha, discount = args.epsilon, args.learning_rate, args.discount
	episodes = args.episodes

	player_strategy = {LEFT : args.left_player_strategy, RIGHT : args.right_player_strategy}
	left_scores, right_scores = [], []

	for episode in range(1, episodes + 1):
	
		ball_pos, ball_dir, left_paddle, right_paddle = reset_game(player_strategy)
		scores = [0, 0]

		left_score = 0
		right_score = 0

		epsilon *= 0.9

		while ENDING_SCORE not in scores:
			print(top_left + WIDTH * "━" + top_right)

			left_state = (left_paddle.line, tuple(ball_pos), tuple(ball_dir))
			left_actions = left_paddle.available_actions()

			left_action = get_action(LEFT, player_strategy, Q, left_player_combinations, left_state, left_actions, epsilon)
			left_player_combinations[left_state, left_action] = True
		
			left_paddle.move(left_action)

			right_state = (right_paddle.line, tuple([ball_pos[0], WIDTH - ball_pos[1] + 1]), tuple([ball_dir[0], -ball_dir[1]]))
			right_actions = right_paddle.available_actions()

			right_action = get_action(RIGHT, player_strategy, Q, right_player_combinations, right_state, right_actions, epsilon)
			right_player_combinations[right_state, right_action] = True

			right_paddle.move(right_action)
			
			for i in range(1, HEIGHT + 1):
				draw_line(ball_pos, i, [left_paddle, right_paddle])			

			print(bottom_left + WIDTH * "━" + bottom_right)	

			result = update_ball_state(ball_pos, ball_dir, [left_paddle, right_paddle])
			scores, ball_pos, ball_dir = result[0], result[1], result[2] 

			reward = scores[LEFT]

			left_score += reward
			right_score += scores[1]

			print('Reward for LEFT player:', reward)

			next_state = (left_paddle.line, tuple(ball_pos), tuple(ball_dir))
			next_legal_actions = left_paddle.available_actions()

			next_action = best_action(Q, next_state, next_legal_actions)

			if (left_state, left_action) not in Q:
				Q[left_state, left_action] = 0

			if (next_state, next_action) not in Q:
				Q[next_state, next_action] = 0

			Q[left_state, left_action] = (1 - alpha) * Q[left_state, left_action] + alpha * (reward + discount * Q[next_state, next_action])

			time.sleep(0 if left_score <= 10 else 0.05)
			os.system('clear')

			print('[{} vs. {} - Episode {}] Q Value: {}'.format(player_strategy[LEFT], player_strategy[RIGHT], episode, Q[left_state, left_action]))

			if left_score >= 20:
				break

		left_scores.append(left_score)
		right_scores.append(right_score)

	plt.ylabel('Score')
	plt.xlabel('Episode')

	plt.plot([i for i in range(1, episodes + 1)], left_scores, 'b')

	plot_name = '[{} vs {}] -- [alpha = {}], [discount = {}], [eps = {}], [episodes = {}].png'
	plt.savefig(plot_name.format(player_strategy[LEFT], player_strategy[RIGHT], alpha, discount, args.epsilon, args.episodes))

if __name__ == '__main__':
	parser = ArgumentParser()

	parser.add_argument('--learning_rate', type=float, default=1)
	parser.add_argument('--discount', type=float, default=0.99)
	parser.add_argument('--epsilon', type=float, default=0.05)
	parser.add_argument('--episodes', type=int, default=10000)
	parser.add_argument('--left_player_strategy', type=str, default='greedy')
	parser.add_argument('--right_player_strategy', type=str, default='e_greedy')

	q_learning(parser.parse_args())