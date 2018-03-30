# Q-Learning-Pong-Agents

Implementation of greedy and e-greedy intelligent pong players. The sizes of the paddles and board can be customized by changing the HEIGHT and WIDTH parameters and the paddle initialization from the reset_game() routine.

Inside the main section of the 'pong.py' source you may find all the configurations that may be used for the players' strategies and the hyperparameters of the Q-Learning algorithm (learning rate, discount, epsilon value).

Running 'python3 pong.py' will initialize a pong game between a greedy and an e-greedy opponent, where the greedy opponent is the one on the left side. The player on the left side will always be the one to do the actual learning and modifying of the Q values, but the opponent may learn of useful movements by checking if states that are symmetric to his have already been explored by the left player.

Inside the 'q_learning()' function you may notice that I use 'time.sleep(0 if left_score <= 10 else 0.05)'. This is done in order to skip visualizing episodes in which the agent performs poorly and wait until it has had enough training to hit the ball at least 10 times in a round.
