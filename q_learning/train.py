import torch
import numpy as np
from kaggle_environments import make
from model import BattleBot, Game, load_bot, Memory
from connect4 import Connect4

LEARNING_RATE = 0.001

def play_battle_bots(board, env, memory, player_1_bot, player_2_bot):
    print('Playing Battle Bots...')

    # Reset the environment and get the initial state of the board
    trainer = env.train([None, 'random'])
    memory.clear()
    observation = trainer.reset()['board']

    # Reset the models for both players and decay the epsilon value
    players = (player_1_bot, player_2_bot)
    for player in players:
        print(player)
        player.reward = 0
        player.decay_epsilon()

    current_player = None
    overflow = False
    actions = []
    i = 0
    while True:
        # Player 1 and Player 2 alternate taking turns
        if i % 2 == 0:
            current_player = player_1_bot
        else:
            current_player = player_2_bot

        # Find the next action for the player to take
        action, _ = board.get_action(current_player, observation, current_player.epsilon)
        # Add the action to the list of actions taken along with the player's name
        actions.append((current_player.name, action))

        # Take the step on the current state of the board
        # and observe the new board state
        try:
            next_observation, _, overflow, _ = trainer.step(action)
        except Exception:
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

        board.print_board(observation)

        # If the board got overflowed, return the player bots, actions, and report that no winner was found
        if reward == -99 and overflow:
            return player_1_bot, player_2_bot, actions, 'NotValidWinnerID'
        else:
            current_player.reward += reward

        memory.add_to_memory(observation, action, reward)

        # Update the model of both battle bots after the game is over
        if winner_found:
            print("Winner Found, Updating models...")
            player_1_bot.train_step(
                    observations=torch.cat(memory.observations),
                    actions=torch.tensor(memory.actions),
                    rewards = torch.tensor(memory.rewards))
            
            player_2_bot.train_step(
                    observations=torch.cat(memory.observations),
                    actions=torch.tensor(memory.actions),
                    rewards = torch.tensor(memory.rewards))

            break

        i += 1

    return player_1_bot, player_2_bot, actions, current_player.bot_id


if __name__ == '__main__':
    env = make("connectx", debug=True)
    memory = Memory()

    # Load the bots for both players
    player_1_bot_id = 'A'
    player_1_bot_name = 'BattleBotA'
    player_1_bot = load_bot(player_1_bot_id)
    if player_1_bot is None:
        print('Creating new bot for player 1...')
        player_1_bot = BattleBot(player_1_bot_name, player_1_bot_id, f'./models/{player_1_bot_name}.pt', None)
        player_1_bot.save_bot()

    player_2_bot_id = 'B'
    player_2_bot_name = 'BattleBotB'
    player_2_bot = load_bot(player_2_bot_id)
    if player_2_bot is None:
        print('Creating new bot for player 2...')
        player_2_bot = BattleBot(player_2_bot_name, player_2_bot_id, f'./models/{player_2_bot_name}.pt', None)
        player_2_bot.save_bot()

    # Create the Connect 4 board
    board = Connect4()

    # Have the two battle bots from the players compete against each other
    player_1_bot, player_2_bot, actions, winner_id = play_battle_bots(board, env, memory, player_1_bot, player_2_bot)

    if winner_id == player_1_bot.bot_id:
        winner_name = player_1_bot.name
        player_1_bot.win_count += 1
    elif winner_id == player_2_bot.bot_id:
        winner_name = player_2_bot.name
        player_2_bot.win_count += 1

    if winner_id == 'NotValidWinnerID':
        winner_name = 'No Winner Found'

    player_1_bot.total_games += 1
    player_2_bot.total_games += 1

    # Update the player models associated with each player
    player_1_bot.save_bot()
    player_2_bot.save_bot()

    print(f'Winner: {winner_name}!!!')

    # Save the game to the database
    game_id = '1'
    game = Game(game_id, player_1_bot.bot_id, player_2_bot.bot_id, winner_name, actions)
    game.save_game()

