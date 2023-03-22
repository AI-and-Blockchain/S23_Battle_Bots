from getAction import get_action

#https://gist.github.com/leeschmalz/7e41fa39a9d734b3483dcfeef55efc9a
def check_if_action_valid(obs, action):
    if obs[action] == 0:
        valid = True
    else:
        valid = False
    return valid

def player_1_agent(observation, player_1_model):
    action, prob_weights = get_action(player_1_model,observation['board'],0)
    if check_if_action_valid(observation['board'],action):
        return action
    else:
        while True:
            previous_prob_weight = prob_weights[action]
            temp_prob = min(prob_weights)
            for prob in prob_weights:
                if prob < previous_prob_weight and prob > temp_prob:
                    temp_prob = prob
                    action = list(prob_weights).index(temp_prob)
            if check_if_action_valid(observation['board'],action):
                break
            
    return action