#https://gist.github.com/leeschmalz/45d2c2d1f6fd15a0f7a64e71740f6fd4
def check_if_done(observation):
    done = [False,'No Winner Yet']
    #horizontal check
    for i in range(6):
        for j in range(4):
            if observation[i][j] == observation[i][j+1] == observation[i][j+2] == observation[i][j+3] == 1:
                done = [True,'Player 1 Wins Horizontal']
            if observation[i][j] == observation[i][j+1] == observation[i][j+2] == observation[i][j+3] == 2:
                done = [True,'Player 2 Wins Horizontal']
    #vertical check
    for j in range(7):
        for i in range(3):
            if observation[i][j] == observation[i+1][j] == observation[i+2][j] == observation[i+3][j] == 1:
                done = [True,'Player 1 Wins Vertical']
            if observation[i][j] == observation[i+1][j] == observation[i+2][j] == observation[i+3][j] == 2:
                done = [True,'Player 2 Wins Vertical']
    #diagonal check top left to bottom right
    for row in range(3):
        for col in range(4):
            if observation[row][col] == observation[row + 1][col + 1] == observation[row + 2][col + 2] == observation[row + 3][col + 3] == 1:
                done = [True,'Player 1 Wins Diagonal']
            if observation[row][col] == observation[row + 1][col + 1] == observation[row + 2][col + 2] == observation[row + 3][col + 3] == 2:
                done = [True,'Player 2 Wins Diagonal']
    
    #diagonal check bottom left to top right
    for row in range(5, 2, -1):
        for col in range(3):
            if observation[row][col] == observation[row - 1][col + 1] == observation[row - 2][col + 2] == observation[row - 3][col + 3] == 1:
                done = [True,'Player 1 Wins Diagonal']
            if observation[row][col] == observation[row - 1][col + 1] == observation[row - 2][col + 2] == observation[row - 3][col + 3] == 2:
                done = [True,'Player 2 Wins Diagonal']
    return done