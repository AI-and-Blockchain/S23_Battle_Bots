import os
import torch
import io
import torch.nn as nn
import torch.optim as optim
import pymongo
from pymongo import MongoClient
class MyMongoDB:
    '''
    mydb = MyMongoDB("mydatabase", "mycollection")

    data = {"name": "John", "age": 30, "city": "New York"}
    inserted_id = mydb.insert_data(data)
    print("Inserted document with ID:", inserted_id)

    all_data = mydb.get_data()
    print("All documents in collection:", all_data)

    query = {"name": "John"}
    john_data = mydb.get_data(query)
    print("Documents with name='John':", john_data)

    query = {"name": "John"}
    deleted_count = mydb.delete_data(query)
    print("Deleted", deleted_count, "documents from collection")

    query = {"name": "John"}
    new_data = {"age": 35}
    modified_count = mydb.update_data(query, new_data)
    print("Modified", modified_count, "documents in collection")
    '''
    def __init__(self, db_name, collection_name):
        self.client = MongoClient('mongodb://localhost:27017')
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
    def insert_data(self, data):
        result = self.collection.insert_one(data)
        return result.inserted_id
        
    def get_data(self, query=None):
        if query:
            data = []
            for doc in self.collection.find(query):
                data.append(doc)
            return data
        else:
            return list(self.collection.find())

    def delete_data(self, query):
        result = self.collection.delete_one(query)
        return result.deleted_count
        
    def update_data(self, query, data):
        result = self.collection.update_one(query, {"$set": data})
        return result.modified_count


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

    def decay_epsilon(self):
        self.epsilon = self.epsilon * 0.99985

    def reset(self):
        self.win_count = 0
        self.reward = 0


def load_player_model(player_model_id, player_model_name, db):
    # TODO: Lookup the player model in the blockchain/Oracle
    # TODO: Return it, if found. Otherwise, return a new model
    query = {'model_id': player_model_id, 'model_name': player_model_name}
    response = db.get_data(query)
    retrieved_model = None

    if response:
        model_data = response['model']
        retrieved_model.model.load_state_dict(torch.load(io.BytesIO(model_data)))
    else:
        print(f'Could not find player model with id {player_model_id} and name {player_model_name}')
        print('Creating a new one from scratch with random weights...')
        retrieved_model = Model(player_model_name)

    return retrieved_model

def save_player_model(player_model_id, player_model_name, player_model, db):
    # TODO: Save the player model to the blockchain/Oracle
    # Save the model to a file
    if not os.path.exists('./models'):
        os.makedirs('./models')

    model_file_path = f'./models/{player_model_name}.pt'
    torch.save(player_model, model_file_path)

    # Load the saved model into memory as binary data
    with open(model_file_path, "rb") as f:
        model_data = f.read()

    # Insert the model data into MongoDB
    data = {'model_id': player_model_id, 'model_name': player_model_name, 'model': model_data}
    inserted_id = db.insert_data(data)
    print("Inserted document with ID:", inserted_id)

    return inserted_id

def save_actions(player_model_id, actions, db):
    # TODO: Save the actions to the blockchain/Oracle
    query = {'model_id': player_model_id, 'actions': actions}
    response = db.insert_data(query)
    print("Inserted document with ID:", response)
    return response

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