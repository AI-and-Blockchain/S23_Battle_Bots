#https://gist.github.com/leeschmalz/14eddfcd5c6dac5cd19e0b400b1e36c1
from kaggle_environments import evaluate, make, utils
env = make("connectx", debug=True)

env.run(['random', 'random'])
env.render(mode="ipython", width=600, height=500, header=False)