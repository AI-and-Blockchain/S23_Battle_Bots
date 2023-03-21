import numpy as np
import tensorflow as tf

#https://gist.github.com/leeschmalz/15dee812ce23d61448fde424c6a6a6e8
def get_action(model, observation, epsilon):
    #determine whether model action or random action based on epsilon
    act = np.random.choice(['model','random'], 1, p=[1-epsilon, epsilon])[0]
    observation = np.array(observation).reshape(1,6,7,1)
    logits = model.predict(observation)
    prob_weights = tf.nn.softmax(logits).numpy()
    
    if act == 'model':
        action = list(prob_weights[0]).index(max(prob_weights[0]))
    if act == 'random':
        action = np.random.choice(7)
        
    return action, prob_weights[0]