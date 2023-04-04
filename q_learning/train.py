import torch
import numpy as np
from kaggle_environments import make
from model import load_player_model, save_player_model, save_actions, Memory
from connect4 import Connect4

LEARNING_RATE = 0.001

def play_battle_bots(board, env, memory, player_1_model, player_2_model):
    print('Playing Battle Bots...')

    # Reset the environment and get the initial state of the board
    trainer = env.train([None, 'random'])
    memory.clear()
    observation = trainer.reset()['board']

    # Reset the models for both players and decay the epsilon value
    players = (player_1_model, player_2_model)
    for player in players:
        player.reset()
        player.decay_epsilon()

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
        # Add the action to the list of actions taken along with the player's name
        actions.append((current_player.name, action))

        # Take the step on the current state of the board
        # and observe the new board state
        try:
            next_observation, _, overflow, _ = trainer.step(action)
        except FailedPrecondition:
            observation = trainer.reset()['board']
            memory.clear()

        observation = next_observation['board']
        observation = torch.tensor(observation, dtype=torch.float32).unsqueeze(0)

        # Check if a player won
        done = board.check_if_done(np.array(observation).reshape(6, 7))
        winner_found, _ = done

        # Update the current state of rewards for both players based
        # on the new, updated board state
        reward = board.find_rewards(done, overflow)
        current_player.reward += reward

        memory.add_to_memory(observation, action, reward)

        # Update the model of both battle bots after the game is over
        if winner_found:
            print("Winner Found, Updating models...")
            player_1_model.train_step(
                    observations=torch.cat(memory.observations),
                    actions=torch.tensor(memory.actions),
                    rewards = torch.tensor(memory.rewards))
            
            player_2_model.train_step(
                    observations=torch.cat(memory.observations),
                    actions=torch.tensor(memory.actions),
                    rewards = torch.tensor(memory.rewards))

            break

        i += 1

    return player_1_model, player_2_model, actions, current_player

if __name__ == '__main__':
    env = make("connectx", debug=True)
    memory = Memory()

    # Load the models for both players
    player_1_model_id = 'A'
    player_1_model_name = 'Player 1'
    player_1_model = load_player_model(player_1_model_id, player_1_model_name)


    player_2_model_id = 'B'
    player_2_model_name = 'Player 2'
    player_2_model = load_player_model(player_2_model_id, player_2_model_name)

    # Create the Connect 4 board
    board = Connect4()

    # Have the two battle bots from the players compete against each other
    new_player_1_model, new_player_2_model, actions = play_battle_bots(board, env, memory, player_1_model, player_2_model)

    # Update the player models associated with each player
    save_player_model(player_1_model_id, player_1_model_name, new_player_1_model)
    save_player_model(player_2_model_id, player_2_model_name, new_player_2_model)

    # Save the actions for the game associated with each player
    save_actions(player_1_model_id, actions)
    save_actions(player_2_model_id, actions)
