import os
import torch
import json
import torch.nn as nn
import torch.optim as optim


#https://gist.github.com/leeschmalz/1b733278792ce751f0a9c2d2de3323b0
class Memory:
    '''Memory buffer for storing the observations, actions, and rewards'''
    def __init__(self):
        self.clear()

    def clear(self):
        '''Clears the memory buffer'''
        self.observations = []
        self.actions = []
        self.rewards = []
        self.info = []
        
    def add_to_memory(self, new_observation, new_action, new_reward):
        '''Adds the new observation, action, and reward to the memory buffer'''
        self.observations.append(new_observation)
        self.actions.append(new_action)
        self.rewards.append(float(new_reward))


class BattleBot:
    '''A battle bot that can play the game of Connect 4'''
    def __init__(self, name, bot_id, model_path, model):
        self.name = name
        self.bot_id = bot_id
        self.model_path = model_path
        self.bots_file_path = './q_learning/bots.json'
        self.epsilon = 1
        self.total_reward = 0
        self.name = name
        self.win_count = 0
        self.total_games = 0
        self.games = []
        self.avg_reward = 0

        # Create the model for the battle bot if one was not passed in
        if model is None:
            self.model = self.create_model()
        else:
            self.model = model

        # Create the optimizer for the model, using the Adam optimizer
        self.optimizer = optim.Adam(self.model.parameters())

        # Initialize the bots data file if it does not exist
        if not os.path.exists(self.bots_file_path):
            with open(self.bots_file_path, "w") as f:
                json.dump([], f)

        # Initialize the models directory if it does not exist
        if not os.path.exists('./q_learning/models'):
            os.makedirs('./q_learning/models')

    def save_bot(self):
        '''Saves the battle bot to the bots data file'''
        with open(self.bots_file_path, "r") as f:
            bots_data = json.load(f)

        if self.total_games > 0:
            self.avg_reward = self.total_reward / self.total_games

        bot_data = {
            "bot_id": self.bot_id,
            "name": self.name,
            "win_count": self.win_count,
            "total_games": self.total_games,
            "epsilon": self.epsilon,
            "total_reward": self.total_reward,
            "avg_reward": self.avg_reward,
            "model_path": self.model_path,
            "games": self.games
        }

        # Check if the bot already exists in the bots data file
        prev_bot = load_bot(self.bot_id)
        if prev_bot is None:
            # If the bot does not exist, add it to the bots data file
            bots_data.append(bot_data)
        else:
            # If the bot does exist, update the bot's data in the bots data file
            for bot_data in bots_data:
                if bot_data['bot_id'] == self.bot_id:
                    bot_data['win_count'] = self.win_count
                    bot_data['total_games'] = self.total_games
                    bot_data['epsilon'] = self.epsilon
                    bot_data['total_reward'] = self.total_reward
                    bot_data['avg_reward'] = self.avg_reward
                    bot_data['games'] = self.games
                    break

        # Save the bots data file with the updated bots list
        with open(self.bots_file_path, "w") as f:
            json.dump(bots_data, f)

        print("Inserted bot document with ID:", self.bot_id)

        # Actually save the model
        torch.save(self.model, self.model_path)


    def create_model(self):
        # Create the model for the battle bot using a simple deep fully connected neural network
        model = nn.Sequential(
            nn.Linear(42, 50),
            nn.ReLU(),
            nn.Linear(50, 50),
            nn.ReLU(),
            nn.Linear(50, 50),
            nn.ReLU(),
            nn.Linear(50, 50),
            nn.ReLU(),
            nn.Linear(50, 50),
            nn.ReLU(),
            nn.Linear(50, 50),
            nn.ReLU(),
            nn.Linear(50, 7)
        )

        return model
    
    def compute_loss(self, logits, actions, rewards):
        # Compute the loss using the logits, actions, and rewards
        log_probs = torch.nn.functional.log_softmax(logits, dim=1)
        action_log_probs = log_probs.gather(1, actions.unsqueeze(1)).squeeze(1)
        loss = -1 * (action_log_probs * rewards).mean()
        return loss

    def train_step(self, observations, actions, rewards):
        # Take a train step for the model using the observations, actions, and rewards
        self.optimizer.zero_grad()
        observations = observations.view(-1, 42).to(torch.float32)
        logits = self.model(observations)
        loss = self.compute_loss(logits, actions, rewards)
        loss.backward()
        self.optimizer.step()

    def decay_epsilon(self):
        # Decay the epsilon value for the battle bot
        # Overtime the battle bot will become more greedy and less random
        self.epsilon = self.epsilon * 0.99985


class Game:
    '''Stores a game of Connect 4, including the game ID, player IDs, winner ID, and actions.'''
    def __init__(self, game_id, player_1_id, player_2_id, winner_id, actions):
        self.game_id = game_id
        self.player_1_id = player_1_id
        self.player_2_id = player_2_id
        self.winner_id = winner_id
        self.actions = actions
        self.games_file_path = './q_learning/games.json'

        # Initialize the games data file if it does not exist
        if not os.path.exists(self.games_file_path):
            with open(self.games_file_path, "w") as f:
                json.dump([], f)

    def save_game(self):
        '''Saves the game to the games data file'''
        # Save the game to the games data file
        with open(self.games_file_path, "r") as f:
            games_data = json.load(f)

        game_data = {
            "game_id": self.game_id,
            "player_1_id": self.player_1_id,
            "player_2_id": self.player_2_id,
            "winner_id": self.winner_id,
            "actions": self.actions,
        }

        # Check if the game already exists in the games data file
        prev_game = load_game(self.game_id)
        if prev_game is None: 
            # If the game does not exist, add it to the games data file
            games_data.append(game_data)
        else:
            # If the game does exist, update the game's data in the games data file
            for game_data in games_data:
                if game_data['game_id'] == self.game_id:
                    game_data['winner_id'] = self.winner_id
                    game_data['actions'] = self.actions
                    break

        # Save the games data file with the updated games list
        with open(self.games_file_path, "w") as f:
            json.dump(games_data, f)

        print("Inserted game document with ID:", self.game_id)


class Trainer:
    '''This class is responsible for setting up the training environment for the battle bots.
    It replaces the kaggle connect4 environment through our own, more flexible environment.'''
    def __init__(self):
        self.num_rows = 6
        self.num_cols = 7
        self.board = []

        # Initialize the board
        for _ in range(self.num_rows):
            self.board.append([0] * self.num_cols)

    def reset(self):
        '''Reset the board to all zeros.'''
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.board[i][j] = 0

    def column_overflow(self, action):
        '''Check if the column has overflowed for the given action.'''
        assert(action >= 0 and action < self.num_cols)
        # If any of the top row is non-zero, then the board has overflowed
        for i in range(self.num_rows):
            if self.board[i][action] == 0:
                return False

        return True

    def step(self, action, player):
        '''Take a step on the board for the given player. Takes the action in that given column.'''
        assert(player == 1 or player == 2)
        assert(action >= 0 and action < self.num_cols)

        # If the column is full, then the action is invalid
        # That means there is no room in that given column for the current action
        if self.column_overflow(action):
            return False

        # Place the player's token in the top of the given column, if there is room
        # Falls as if there is gravity
        for i in range(self.num_rows - 1, -1, -1):
            if self.board[i][action] == 0:
                self.board[i][action] = player
                return True

        return False


def load_bot(bot_id):
    '''Loads a bot from the bots data file using the bot ID.'''
    # Initialize the bots data file if it does not exist
    if not os.path.exists('./q_learning/bots.json'):
        with open('./q_learning/bots.json', "w") as f:
            json.dump([], f)

    # Load the bots data file
    with open('./q_learning/bots.json', "r") as f:
        bots_data = json.load(f)

    # Find the bot with the given bot ID
    for bot_data in bots_data:
        if bot_data['bot_id'] == bot_id:
            print("Found bot with bot_id", bot_id)

            # Recreate the bot object using the bot data
            bot_id, name, win_count, total_games, epsilon, total_reward, avg_reward, model_path, games = bot_data.values()
            bot = BattleBot(name, bot_id, model_path, torch.load(model_path))
            bot.win_count = win_count
            bot.total_games = total_games
            bot.epsilon = epsilon
            bot.total_reward = total_reward
            bot.avg_reward = avg_reward
            bot.games = games

            return bot

    print("Bot with bot_id", bot_id, "not found")
    return None

def delete_bot(bot_id):
    '''Finds a bot from the bots data file using the bot ID and
    deletes it.'''
    # Initialize the bots data file if it does not exist
    if not os.path.exists('./q_learning/bots.json'):
        with open('./q_learning/bots.json', "w") as f:
            json.dump([], f)

    # Load the bots data file
    with open('./q_learning/bots.json', "r") as f:
        bots_data = json.load(f)

    # Find the bot with the given bot ID
    for bot_data in bots_data:
        if bot_data['bot_id'] == bot_id:
            print("Found bot with bot_id", bot_id)

            # Remove the bot from the bots data file
            bots_data.remove(bot_data)
            return True

    print("Bot with bot_id", bot_id, "not found")
    return None

def load_game(game_id):
    '''Loads a game from the games data file using the game ID.'''
    if not os.path.exists('./q_learning/games.json'):
        with open('./q_learning/games.json', "w") as f:
            json.dump([], f)

    # Load the games data file
    with open('./q_learning/games.json', "r") as f:
        games_data = json.load(f)

    # Find the game with the given game ID
    for game_data in games_data:
        if game_data['game_id'] == game_id:
            print("Found game with game_id", game_id)

            # Recreate the game object using the game data
            game_id, player_1_id, player_2_id, winner_id, actions = game_data.values()
            game = Game(game_id, player_1_id, player_2_id, winner_id, actions)

            return game

    print("Game with game_id", game_id, "not found")
    return None
