import torch
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
import torch
import torch.nn as nn
import torch.optim as optim

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

    def convert_model(self, model_file_path):
        # Save the model to a file
        torch.save(self.model, model_file_path)

        # Convert the model to a TorchScript model
        traced_model = torch.jit.trace(self.model, torch.randn(1, 1, 28, 28))
        
        # Save the TorchScript model to a file
        traced_model_file_path = f'{model_file_path}/model.pt'
        traced_model.save(traced_model_file_path)

    def decay_epsilon(self):
        self.epsilon = self.epsilon * 0.99985

    def reset(self):
        self.win_count = 0
        self.reward = 0


def load_player_model(player_model_id, player_model_name):
    # TODO: Lookup the player model in the blockchain/Oracle
    # TODO: Return it, if found. Otherwise, return a new model
    # retrieved_model = db.lookup(player_model_id)
    retrieved_model = None

    if retrieved_model is None:
        print(f'Could not find player model with id {player_model_id} and name {player_model_name}')
        print('Creating a new one from scratch with random weights...')
        retrieved_model = Model(player_model_name)

    return retrieved_model

def save_player_model(player_model_id, player_model):
    # TODO: Save the player model to the blockchain/Oracle
    # Return the response
    # response = db.save(player_model_id, player_model)
    # return response
    pass

def save_actions(player_model_id, actions):
    # TODO: Save the actions to the blockchain/Oracle
    # Return the response
    # response = db.save(player_model_id, actions)
    # return response
    pass