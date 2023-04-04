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


def load_player_model(player_model_id, player_model_name):
    # TODO: Lookup the player model in the blockchain/Oracle
    # TODO: Return it, if found. Otherwise, return a new model
    if not os.path.exists('./models.json'):
        with open("models.json", "w") as f:
            json.dump([], f)

    with open("models.json", "r") as f:
        models = json.load(f)

    retrieved_model = None
    for model in models:
        if model['model_id'] == player_model_id and model['model_name'] == player_model_name:
            model_file_path = model['model_file_path']
            retrieved_model = torch.load(model_file_path)

    if retrieved_model is None:
        print(f'Could not find player model with id {player_model_id} and name {player_model_name}')
        print('Creating a new one from scratch with random weights...')
        retrieved_model = Model(player_model_name)

    return retrieved_model

def save_player_model(player_model_id, player_model_name, player_model):
    # TODO: Save the player model to the blockchain/Oracle
    # Save the model to a file
    if not os.path.exists('./models'):
        os.makedirs('./models')

    if not os.path.exists('./models.json'):
        with open("models.json", "w") as f:
            json.dump([], f)

    model_file_path = f'./models/{player_model_name}.pt'
    torch.save(player_model, model_file_path)

    with open("models.json", "r") as f:
        models_data = json.load(f)

    data = {'model_id': player_model_id, 'model_name': player_model_name, 'model_file_path': model_file_path}
    models_data.append(data)

    with open("models.json", "w") as f:
        json.dump(models_data, f)

    print("Inserted document with ID:", player_model_id)

    return player_model_id

def save_actions(player_model_id, actions):
    # TODO: Save the actions to the blockchain/Oracle
    if not os.path.exists('./actions.json'):
        with open("actions.json", "w") as f:
            json.dump([], f)

    with open("actions.json", "r") as f:
        actions_data = json.load(f)

    data = {'model_id': player_model_id, 'actions': actions}
    actions_data.append(data)

    with open("actions.json", "w") as f:
        json.dump(actions_data, f)

    print("Inserted document with ID:", player_model_id)
    
    return player_model_id

def load_actions(player_model_id):
    if not os.path.exists('./actions.json'):
        with open("actions.json", "w") as f:
            json.dump([], f)

    with open("actions.json", "r") as f:
        actions_data = json.load(f)

    actions = None
    for action in actions_data:
        if action['model_id'] == player_model_id:
            actions = action['actions']
    
    print(f'Loaded actions for model id {player_model_id}: {actions}')

    return actions
    

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