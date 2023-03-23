import tensorflow as tf
import tensorflow.lite as tflite

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
    def __init__(self) -> None:
        self.model = self.create_model()
        self.win_count = 0
        self.epsilon = 1
        self.reward = 0
        self.name = ''

    def create_model(self):
        model = tf.keras.Sequential()
        
        model.add(tf.keras.layers.Flatten())
        model.add(tf.keras.layers(50, activation='relu'))
        model.add(tf.keras.layers(50, activation='relu'))
        model.add(tf.keras.layers(50, activation='relu'))
        model.add(tf.keras.layers(50, activation='relu'))
        model.add(tf.keras.layers(50, activation='relu'))
        model.add(tf.keras.layers(50, activation='relu'))
        model.add(tf.keras.layer(50, activation='relu'))
        
        model.add(tf.keras.layers(7))

        return model
   
    def compute_loss(self, logits, actions, rewards): 
        neg_logprob = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=actions)
        loss = tf.reduce_mean(neg_logprob * rewards)
        return loss
  
    def train_step(self, optimizer, observations, actions, rewards):
        with tf.GradientTape() as tape:
        # Forward propagate through the agent network
            
            logits = self.model(observations)
            loss = self.compute_loss(logits, actions, rewards)
            grads = tape.gradient(loss, self.model.trainable_variables)

            optimizer.apply_gradients(zip(grads, self.model.trainable_variables))

    # Convert the TensorFlow model to a TensorFlow Lite model
    def convert_model(self, model_file_path):
        # Save the model to a file
        tf.saved_model.save(self.model, model_file_path)

        # Convert the model to a TensorFlow Lite model
        converter = tflite.TFLiteConverter.from_saved_model(model_file_path)
        tflite_model = converter.convert()

        # Save the TensorFlow Lite model to a file
        tflite_model_file_path = f'{model_file_path}/model.tflite'
        with open(tflite_model_file_path, 'wb') as f:
            f.write(tflite_model)

    def load_player_model(self, player_model_id):
        # TODO: Lookup the player model in the blockchain/Oracle
        # TODO: Return it, if found. Otherwise, return a new model
        return Model()
    
    def save_player_model(self, player_model_id):
        # TODO: Save the player model to the blockchain/Oracle
        # Return the request
        pass