import tensorflow as tf
import numpy as np
from kaggle_environments import make
from model import load_player_model, save_player_model, save_actions, Memory
from connect4 import Connect4


LEARNING_RATE = 0.001


def play_battle_bots(board, env, memory, player_1_model, player_2_model):
    print('Playing Battle Bots...')
    trainer = env.train([None, 'random'])        
    observation = trainer.reset()['board']
    memory.clear()

    player_1_model.epsilon = player_1_model.epsilon * .99985
    player_2_model.epsilon = player_2_model.epsilon * .99985

    player_1_model.reward = 0
    player_2_model.reward = 0

    player_1_model.name = 'Player 1'
    player_2_model.name = 'Player 2'

    current_player = None
    overflow = False
    actions = []
    i = 0
    while True:
        # Player 1 and Player 2 alternate taking turns
        if i % 2 == 0:
            current_player = player_1_model
        else:
            current_player = player_2_model

        # Find the next action for the player to take
        action, _ = board.get_action(current_player, observation, current_player.epsilon)
        # This is another option for getting the action, chooses the next highest probability action
        # when an invalid action is encountered
        # action = board.player_agent_action(current_player, observation)

        # Add the action to the list of actions taken along with the player's name
        actions.append((current_player.name, action))

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
        
        memory.add_to_memory(np.array(observation).reshape(6, 7, 1), action, reward)
        
        # Update the model of both battle bots after the game is over
        if winner_found:
            print("Winner Found, Updating models...")
            player_1_model.train_step(optimizer,
                    observations=np.array(memory.observations),
                    actions=np.array(memory.actions),
                    rewards = memory.rewards)
            
            player_2_model.train_step(optimizer,
                    observations=np.array(memory.observations),
                    actions=np.array(memory.actions),
                    rewards = memory.rewards)
            break

        i += 1

    return player_1_model, player_2_model, actions

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
    new_player_1_model, new_player_2_model, actions = play_battle_bots(board, env, memory, player_1_model, player_2_model)

    save_player_model(player_1_model_id, new_player_1_model)
    save_player_model(player_2_model_id, new_player_2_model)

    save_actions(actions)