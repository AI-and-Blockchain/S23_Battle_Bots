from algosdk import account, encoding, mnemonic
from algosdk.transaction import Transaction
from q_learning.model import BattleBot, Game, load_bot, Memory, Trainer
from q_learning.connect4 import Connect4
from algosdk.v2client import algod
from algosdk.wallet import Wallet
from pyteal import *
from q_learning.train import play_battle_bots
from algosdk.v2client import indexer
import algosdk
import time, os, base64, uuid

# Connect to Algorand node
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "" # PUT TOKEN HERE
headers = {"X-API-KEY": algod_token}
my_client = algod.AlgodClient(algod_token, algod_address, headers)

# Define smart contract information
apid = 0 # PUT APP ID HERE
app_address = "" # PUT APP ADDRESS HERE


# [run game]
# pull model from MongloDB database in model.py and call play_battle_bots in train.py

def runGame(player1ID, player2ID, botID1, botID2):

    memory = Memory()
    # Load the bots for both players
    player_1_bot_id = botID1
    player_1_bot_name = 'BattleBotA'
    player_1_bot = load_bot(player_1_bot_id)

    # If the bot does not exist, create a new one
    if player_1_bot is None:
        print('Creating new bot for player 1...')
        player_1_bot = BattleBot(player_1_bot_name, player_1_bot_id, f'./q_learning/models/{player_1_bot_id}.pt', None)
        player_1_bot.save_bot()

    player_2_bot_id = botID2
    player_2_bot_name = 'BattleBotB'
    player_2_bot = load_bot(player_2_bot_id)

    # If the bot does not exist, create a new one
    if player_2_bot is None:
        print('Creating new bot for player 2...')
        player_2_bot = BattleBot(player_2_bot_name, player_2_bot_id, f'./q_learning/models/{player_2_bot_id}.pt', None)
        player_2_bot.save_bot()

    # Create the Connect 4 board
    board = Connect4()

    # Have the two battle bots from the players compete against each other
    player_1_bot, player_2_bot, actions, winner_id = play_battle_bots(board, memory, player_1_bot, player_2_bot)

    # Save the game to the database
    if winner_id == player_1_bot.bot_id:
        winner_name = player_1_bot.name
        player_1_bot.win_count += 1
    elif winner_id == player_2_bot.bot_id:
        winner_name = player_2_bot.name
        player_2_bot.win_count += 1
    elif winner_id == 'NotValidWinnerID':
        winner_name = 'No Winner Found'

    game_id = str(uuid.uuid4())
    game = Game(game_id, player_1_bot.bot_id, player_2_bot.bot_id, winner_name, actions)
    game.save_game()

    # Print the winner of the Connect 4 Game
    player_1_bot.total_games += 1
    player_2_bot.total_games += 1
    player_1_bot.games.append(game_id)
    player_2_bot.games.append(game_id)

    # Update the player models & battle bots associated with each player
    player_1_bot.save_bot()
    player_2_bot.save_bot()

    print(f'Winner: {winner_name}!!!')

    updateWebsite(player_1_bot_id, player_2_bot_id, actions, winner_id)
    callContract(winner_id)

    pass

# [update and send info]
# with the return from play_battle_bots update models in database, update 
# website with moves, and call smart contract with winner (with word 'resolve'
# as first arguement), winner id must be base32 encoded.
# Connect to Algorand node

def updateWebsite(player1ID, player2ID, actions, winner):
    # send moves and winner to website
    print("Not Implemented")

def callContract(winner):
    """
    # send winner to smart contract

    # Define the parameters for the transaction
    params = my_client.suggested_params()
    params.fee = 1000
    params.flat_fee = True

    # Define the arguments for the transaction
    arguments = ["resolve".encode(), winner.encode()]


    # Build the transaction
    txn = Transaction(
        sender=algod_address,
        sp=params,
        app_id=apid,
        on_complete=OnComplete.NoOpOC.real,
        note=bytes("Winner of the bet".encode()),
        app_args=arguments,
    )
    # Sign the transaction
    signed_txn = txn.sign(algod_token)

    # Send the transaction
    tx_id = algod_client.send_transaction(signed_txn)
    print(f"Transaction ID: {tx_id}")

    """
    print("Not Implemented")


# [recieve game information]
# check algorand blockchain every few seconds and if any users local state's game 
# ready variable is set to 'true' then pull model id and opponent model id

# Define oracle logic
"""
def process_event(event):
    if event['type'] == 'application' and event['application-index'] == program:
    
        # Retrieve the sender and application ID from the event data
        sender = event['txn']['txn']['sender']
        app_id = event['txn']['txn']['application-id']

        # Retrieve the bot and opponent values from local state using the sender and app ID
        bot = algod_client.account_info(sender)['apps-local-state'][str(app_id)][bytes("bot").hex()]
        opponent = algod_client.account_info(sender)['apps-local-state'][str(app_id)][bytes("opponent").hex()]

        # Print the bot and opponent values to the console
        print(f"Bot: {bot}")
        print(f"Opponent: {opponent}")
"""


# Wait for events
def wait_for_events():
    # Initialize the indexer client
    testnet_address = "https://testnet-algorand.api.purestake.io/idx2"
    idx_client = indexer.IndexerClient(algod_token, testnet_address, headers)
    last_txn_id = 28973160
    # Loop indefinitely
    while True:
        print("Searching for Transactions...")
        # Get the transactions of the smart contract with a higher ID than the last processed ID
        txns = idx_client.search_transactions_by_address(
            #application_id=apid,
            address = app_address,
            min_round=last_txn_id + 1
        )

        # Iterate over the new transactions and extract the user ID
        
        opponents = {}
        botid = {}
        for txn in txns["transactions"]:
            #print("transaction\n", txn, "\n")
            local_state = idx_client.lookup_account_application_local_state(txn['sender'], include_all = True)
            for pair in local_state['apps-local-states'][0]['key-value']:
                if base64.b64decode(pair['key']).decode('utf-8') == 'bot':  
                    botid[txn['sender']] = str(int.from_bytes(base64.b64decode(pair['value']['bytes']), 'big'))
            if txn['sender'] in opponents:
                print(botid)
                runGame(txn['sender'], opponents[txn['sender']], botid[txn['sender']], botid[opponents[txn['sender']]])
            else:
                for pair in local_state['apps-local-states'][0]['key-value']:
                    if base64.b64decode(pair['key']).decode('utf-8') == 'opponent':
                        opponents[algosdk.encoding.encode_address(base64.b64decode(pair['value']['bytes']))] = txn['sender']

            # Update the last processed ID
            last_txn_id = max(last_txn_id, txn["confirmed-round"])
        # Wait for a few seconds before checking for new transactions again
        time.sleep(5)

# Main function
def main():
    # Wait for events
    wait_for_events()

if __name__ == "__main__":
    main()
