import numpy as np
import torch
from typing import Tuple
import torch.nn.functional as F

class Connect4:
    def get_action(self, player_model, observation, epsilon):
        #determine whether model action or random action based on epsilon
        act = np.random.choice(['model','random'], 1, p=[1 - epsilon, epsilon])[0]
        observation = torch.from_numpy(np.array(observation)).float().unsqueeze(0)
        logits = player_model.model(observation)
        prob_weights = F.softmax(logits, dim=1).detach().numpy()[0]

        if act == 'model':
            action = list(prob_weights).index(max(prob_weights))
        if act == 'random':
            action = np.random.choice(7)

        return action, prob_weights


    def check_if_done(self, observation):
        done = (False, 'No Winner Yet')
        # vertical check
        for j in range(7):
            for i in range(3):
                if observation[i][j] == observation[i + 1][j] == observation[i + 2][j] == observation[i + 3][j] == 1:
                    done = (True, 'Player 1 Wins Vertical')
                if observation[i][j] == observation[i + 1][j] == observation[i + 2][j] == observation[i + 3][j] == 2:
                    done = (True, 'Player 2 Wins Vertical')

        #horizontal check
        for i in range(6):
            for j in range(4):
                if observation[i][j] == observation[i][j + 1] == observation[i][j + 2] == observation[i][j + 3] == 1:
                    done = (True, 'Player 1 Wins Horizontal')
                if observation[i][j] == observation[i][j + 1] == observation[i][j + 2] == observation[i][j + 3] == 2:
                    done = (True, 'Player 2 Wins Horizontal')

        #diagonal check top left to bottom right
        for row in range(3):
            for col in range(4):
                if observation[row][col] == observation[row + 1][col + 1] == observation[row + 2][col + 2] == observation[row + 3][col + 3] == 1:
                    done = (True, 'Player 1 Wins Diagonal')
                if observation[row][col] == observation[row + 1][col + 1] == observation[row + 2][col + 2] == observation[row + 3][col + 3] == 2:
                    done = (True, 'Player 2 Wins Diagonal')

        #diagonal check bottom left to top right
        for row in range(5, 2, -1):
            for col in range(3):
                if observation[row][col] == observation[row - 1][col + 1] == observation[row - 2][col + 2] == observation[row - 3][col + 3] == 1:
                    done = (True, 'Player 1 Wins Diagonal')
                if observation[row][col] == observation[row - 1][col + 1] == observation[row - 2][col + 2] == observation[row - 3][col + 3] == 2:
                    done = (True, 'Player 2 Wins Diagonal')

        return done
    
    def print_board(self, observation):
        print('=====================')
        for row in observation:
            print("| ", end="")
            for val in row:
                print(str(val) + " | ", end="")
            print("")
            print("-" * (len(row) * 5))
        print('=====================')
  
    # Easiest to Hardest: Vertical (10), Horizontal (20), Diagonal (30)
    def find_rewards(self, done: Tuple[bool, int], overflow: bool):
        assert(done and len(done) == 2)

        winner_found, win_type = done
        if not winner_found and overflow:
            return -99
        if not winner_found:
            return 0
        
        if 'Vertical' in win_type:
            return 10
        elif 'Horizontal' in win_type:
            return 20
        elif 'Diagonal' in win_type:
            return 30

        return 0

    def check_if_action_valid(self, obs, action):
        if obs[action] == 0:
            valid = True
        else:
            valid = False

        return valid

    def player_agent_action(self, observation, player_model):
        action, prob_weights = self.get_action(player_model, observation['board'], 0)
        if self.check_if_action_valid(observation['board'], action):
            return action
        else:
            while True:
                previous_prob_weight = prob_weights[action]
                temp_prob = min(prob_weights)
                for prob in prob_weights:
                    if prob < previous_prob_weight and prob > temp_prob:
                        temp_prob = prob
                        action = list(prob_weights).index(temp_prob)
                if self.check_if_action_valid(observation['board'], action):
                    break
                
        return action
