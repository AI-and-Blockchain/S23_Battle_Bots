import torch
from model import BattleBot, Game, load_bot, Memory, Trainer
from connect4 import Connect4
import uuid

LEARNING_RATE = 0.001

def play_battle_bots(board, memory, player_1_bot, player_2_bot, debug = True):
    print('Playing Battle Bots...')

    # Reset the environment and get the initial state of the board
    trainer = Trainer()
    memory.clear()
    observation = trainer.board

    # Reset the models for both players and decay the epsilon value
    players = (player_1_bot, player_2_bot)
    for player in players:
        player.decay_epsilon()

    current_player = None
    column_overflow = False
    actions = []
    i = 0
    current_player_token = 1
    next_observation = None
    while True:
        # Player 1 and Player 2 alternate taking turns
        if i % 2 == 0:
            current_player = player_1_bot
            current_player_token = 1
        else:
            current_player = player_2_bot
            current_player_token = 2

        # Find the next action for the player to take
        action, _ = board.get_action(current_player, observation, current_player.epsilon)

        # Add the action to the list of actions taken along with the player's name
        actions.append((current_player.bot_id, action))

        # Take the step on the current state of the board
        # and observe the new board state
        try:
            column_overflow = trainer.step(action, current_player_token)
            next_observation = trainer.board
        except Exception as e:
            print('Error in trainer.step: ', e)
            trainer.reset()
            observation = trainer.board
            memory.clear()

        observation = next_observation
        if debug:
            board.print_board(observation)

        # Check if a player won
        done = board.check_if_done(observation)
        winner_found, _ = done

        # Update the current state of rewards for both players based
        # on the new, updated board state
        reward = board.find_rewards(done, column_overflow)

        # If the board got overflowed, return the player bots, actions, and report that no winner was found
        invalid_board = i >= 42 and not winner_found
        if invalid_board:
            return player_1_bot, player_2_bot, actions, 'NotValidWinnerID'
        else:
            current_player.total_reward += reward

        # Add the current state of the board to the memory
        memory.add_to_memory(observation, action, reward)

        # Update the model of both battle bots after the game is over
        if winner_found:
            print("Winner Found, Updating models...")

            # Update the model of both battle bots after the game is over
            player_1_bot.train_step(
                    observations=torch.tensor(memory.observations),
                    actions=torch.tensor(memory.actions),
                    rewards=torch.tensor(memory.rewards))

            player_2_bot.train_step(
                    observations=torch.tensor(memory.observations),
                    actions=torch.tensor(memory.actions),
                    rewards=torch.tensor(memory.rewards))

            break

        i += 1

    return player_1_bot, player_2_bot, actions, current_player.bot_id


if __name__ == '__main__':
    memory = Memory()

    # Load the bots for both players
    player_1_bot_id = 'A'
    player_1_bot_name = 'BattleBotA'
    player_1_bot = load_bot(player_1_bot_id)

    # If the bot does not exist, create a new one
    if player_1_bot is None:
        print('Creating new bot for player 1...')
        player_1_bot = BattleBot(player_1_bot_name, player_1_bot_id, f'./models/{player_1_bot_name}.pt', None)
        player_1_bot.save_bot()

    player_2_bot_id = 'B'
    player_2_bot_name = 'BattleBotB'
    player_2_bot = load_bot(player_2_bot_id)

    # If the bot does not exist, create a new one
    if player_2_bot is None:
        print('Creating new bot for player 2...')
        player_2_bot = BattleBot(player_2_bot_name, player_2_bot_id, f'./models/{player_2_bot_name}.pt', None)
        player_2_bot.save_bot()

    # Create the Connect 4 board
    board = Connect4()

    # Have the two battle bots from the players compete against each other
    player_1_bot, player_2_bot, actions, winner_id = play_battle_bots(board, memory, player_1_bot, player_2_bot)

    # Save the game to the database
    if winner_id == player_1_bot.bot_id:
        winner_name = player_1_bot.name
        player_1_bot.win_count += 1
    elif winner_id == player_2_bot.bot_id:
        winner_name = player_2_bot.name
        player_2_bot.win_count += 1
    elif winner_id == 'NotValidWinnerID':
        winner_name = 'No Winner Found'

    game_id = str(uuid.uuid4())
    game = Game(game_id, player_1_bot.bot_id, player_2_bot.bot_id, winner_name, actions)
    game.save_game()

    # Print the winner of the Connect 4 Game
    player_1_bot.total_games += 1
    player_2_bot.total_games += 1
    player_1_bot.games.append(game_id)
    player_2_bot.games.append(game_id)

    # Update the player models & battle bots associated with each player
    player_1_bot.save_bot()
    player_2_bot.save_bot()

    print(f'Winner: {winner_name}!!!')


