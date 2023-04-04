import os
import torch
import io
import json
import torch.nn as nn
import torch.optim as optim


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

#https://gist.github.com/leeschmalz/fd5535477f276c5e9b965c6c1ea13cbd

class Model:
    def __init__(self, name = '') -> None:
        self.model = self.create_model()
        self.win_count = 0
        self.epsilon = 1
        self.reward = 0
        self.name = name
        self.optimizer = optim.Adam(self.model.parameters())

    def create_model(self):
        model = nn.Sequential(
            nn.Flatten(),
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
        log_probs = torch.nn.functional.log_softmax(logits, dim=1)
        action_log_probs = log_probs.gather(1, actions.unsqueeze(1)).squeeze(1)
        loss = -1 * (action_log_probs * rewards).mean()
        return loss

    def train_step(self, observations, actions, rewards):
        self.optimizer.zero_grad()
        logits = self.model(observations)
        loss = self.compute_loss(logits, actions, rewards)
        loss.backward()
        self.optimizer.step()

    def decay_epsilon(self):
        self.epsilon = self.epsilon * 0.99985

    def reset(self):
        self.win_count = 0
        self.reward = 0


class BattleBot:
    def __init__(self, name, id, model_path, model):
        self.name = name
        self.id = id
        self.model_path = model_path
        self.model = model
        self.bots_file_path = './bots.json'

        if not os.path.exists(self.bots_file_path):
            with open(self.bots_file_path, "w") as f:
                json.dump([], f)

        # Save the model to a file
        if not os.path.exists('./models'):
            os.makedirs('./models')

    def save_bot(self):
        with open(self.bots_file_path, "r") as f:
            bots_data = json.load(f)

        data = {'name': self.name, 'id': self.id, 'model_path': self.model_path}
        bots_data.append(data)

        with open(self.bots_file_path, "w") as f:
            json.dump(bots_data, f)

        print("Inserted bot document with ID:", self.id)

        # Actually save the model
        torch.save(self.model, self.model_path)

    def update_model(self, model):
        self.model = model
        self.save_bot()


class Game:
    def __init__(self, id, player_1, player_2, winner, actions):
        self.id = id
        self.player_1 = player_1
        self.player_2 = player_2
        self.winner = winner
        self.actions = actions
        self.games_file_path = './games.json'

        if not os.path.exists(self.games_file_path):
            with open(self.games_file_path, "w") as f:
                json.dump([], f)

    def save_game(self):
        with open(self.games_file_path, "r") as f:
            games_data = json.load(f)

        data = {'id': self.id, 'player_1': self.player_1, 'player_2': self.player_2, 'winner': self.winner, 'actions': self.actions}
        games_data.append(data)

        with open(self.games_file_path, "w") as f:
            json.dump(games_data, f)

        print("Inserted game document with ID:", self.id)


def load_bot(id):
    if not os.path.exists('./bots.json'):
        with open('./bots.json', "w") as f:
            json.dump([], f)

    with open('./bots.json', "r") as f:
        bots_data = json.load(f)

    for bot in bots_data:
        if bot['id'] == id:
            print("Found bot with id", id)
            return bot

    print("Bot with id", id, "not found")
    return None

def load_game(id):
    if not os.path.exists('./games.json'):
        with open('./games.json', "w") as f:
            json.dump([], f)

    with open('./games.json', "r") as f:
        games_data = json.load(f)

    for game in games_data:
        if game['id'] == id:
            print("Found game with id", id)
            return game

    print("Game with id", id, "not found")
    return None

'''TODO:
1. a function that returns the winner of the game given two model ids
2. a function that given an id creates a new model and stores it with that id
3. a function that given a model id deletes the model
'''

def get_winner(model_id_1, model_id_2):
    pass

def create_new_model(model_id):
    pass

def delete_model(model_id):
    pass