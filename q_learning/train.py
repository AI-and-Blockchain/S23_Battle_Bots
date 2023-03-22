import tensorflow as tf
import numpy as np
from getAction import get_action
from checkIfDone import 
from kaggle_environments import make
from model import create_model, train_step, Model, load_player_model
from connect4 import Connect4

LEARNING_RATE = 0.001

#https://gist.github.com/leeschmalz/1b733278792ce751f0a9c2d2de3323b0
class Memory:
    def __init__(self): 
        self.clear()

    # Resets/restarts the memory buffer
    def clear(self): 
        self.observations = []
        self.actions = []
        self.rewards = []
        self.info = []
        
    def add_to_memory(self, new_observation, new_action, new_reward): 
        self.observations.append(new_observation)
        self.actions.append(new_action)
        self.rewards.append(float(new_reward))


def play_battle_bots(board, env, memory, player_1_model, player_2_model):
    trainer = env.train([None, None])        
    observation = trainer.reset()['board']
    memory.clear()

    player_1_model.epsilon = player_1_model.epsilon * .99985
    player_2_model.epsilon = player_2_model.epsilon * .99985

    player_1_model.reward = 0
    player_2_model.reward = 0

    current_player = None
    overflow = False
    i = 0
    while i:
        # Player 1 and Player 2 alternate taking turns
        if i % 2 == 0:
            current_player = player_1_model
        else:
            current_player = player_2_model

        # Find the next action for the player to take
        action, _ = board.get_action(current_player, observation, epsilon)

        # Take the step on the current state of the board
        # and observe the new board state
        next_observation, _, overflow, _ = trainer.step(action)
        observation = next_observation['board']
        observation = [float(i) for i in observation]

        # Check if a player won
        done = board.check_if_done(np.array(observation).reshape(6, 7))
        winner_found, _ = done

        # Update the current state of rewards for both players based
        # on the new, updated board state
        reward = board.find_rewards(done, overflow)
        current_player.reward += reward
        
        memory.add_to_memory(np.array(observation).reshape(6,7,1), action, reward)
        
        # Update the model of both battle bots after the game is over
        if winner_found:
            train_step(player_1_model, optimizer,
                    observations=np.array(memory.observations),
                    actions=np.array(memory.actions),
                    rewards = memory.rewards)
            
            train_step(player_2_model, optimizer,
                    observations=np.array(memory.observations),
                    actions=np.array(memory.actions),
                    rewards = memory.rewards)
            break

        i += 1

if __name__ == '__main__':
    #train player 1 against random agent
    tf.keras.backend.set_floatx('float64')
    optimizer = tf.keras.optimizers.Adam(LEARNING_RATE)

    env = make("connectx", debug=True)
    memory = Memory()

    player_1_model_id = 'A'
    player_1_model = load_player_model(player_1_model_id)

    player_2_model_id = 'B'
    player_2_model = load_player_model(player_2_model_id)

    board = Connect4()
    play_battle_bots(board, env, memory, player_1_model, player_2_model)
    # epsilon = 1
    # win_count = 0

    # player_1_model = Model()
    # player_2_model = Model()

    for i_episode in range(40000):
        
        trainer = env.train([None,'random'])
            
        observation = trainer.reset()['board']
        memory.clear()
        epsilon = epsilon * .99985
        overflow = False
        while True:
            action, _ = get_action(player_1_model,observation,epsilon)
            next_observation, dummy, overflow, info = trainer.step(action)
            observation = next_observation['board']
            observation = [float(i) for i in observation]
            done = check_if_done(np.array(observation).reshape(6,7))
            
            #-----Customize Rewards Here------
            if done[0] == False:
                reward = 0
            if 'Player 2' in done[1]:
                reward = -20
            if 'Player 1' in done[1]:
                win_count += 1
                reward = 20
            if overflow == True and done[0] == False:
                reward = -99
                done[0] = True
            #-----Customize Rewards Here------
            
            memory.add_to_memory(np.array(observation).reshape(6,7,1), action, reward)
            if done[0]:
                #train after each game
                
                train_step(player_2_model, optimizer,
                        observations=np.array(memory.observations),
                        actions=np.array(memory.actions),
                        rewards = memory.rewards)
                
                break

