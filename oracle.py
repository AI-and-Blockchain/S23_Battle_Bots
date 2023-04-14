from algosdk import account, encoding, mnemonic, transaction
from q_learning.model import BattleBot, Game, load_bot, delete_bot, Memory
from q_learning.connect4 import Connect4
from algosdk.v2client import algod
from pyteal import *
from q_learning.train import play_battle_bots
from algosdk.v2client import indexer
import algosdk
import time, base64, uuid, os, json

# Connect to Algorand node
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "" # PUT TOKEN HERE
headers = {"X-API-KEY": algod_token}
my_client = algod.AlgodClient(algod_token, algod_address, headers)

# Define smart contract information
apid = 190912038 # PUT APP ID HERE
app_address = "" # PUT APP ADDRESS HERE

privateKey = "" #private key for sending winner
publicAdd = "" #public key for sending winner
pa = encoding.decode_address(publicAdd)

gameDone = True
# [run game]

def deleteBot(botID):
    print(delete_bot(botID))
    
def runGame(player1ID, player2ID, botID1, botID2):
    gameDone = False
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
        callContract(player1ID, player1ID, player2ID, False)
    elif winner_id == player_2_bot.bot_id:
        winner_name = player_2_bot.name
        player_2_bot.win_count += 1
        callContract(player2ID, player1ID, player2ID, False)
    elif winner_id == 'NotValidWinnerID':
        winner_name = 'No Winner Found'
        callContract(winner_id, player1ID, player2ID, True)

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

    gameDone = True

# [update and send info]
# with the return from play_battle_bots update models in database, update 
# website with moves, and call smart contract with winner (with word 'resolve'
# as first arguement), winner id must be base32 encoded.
# Connect to Algorand node

def wait_for_confirmation(client, txid):
    last_round = client.status().get("last-round")
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get("confirmed-round") and txinfo.get("confirmed-round") > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print(
        "Transaction {} confirmed in round {}.".format(
            txid, txinfo.get("confirmed-round")
        )
    )
    return txinfo

def call_app(client, private_key, pub,index, app_args, player1ID, player2ID):
    # declare sender
    sender = pub
    print("Call from account:", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args,accounts=[player1ID,player2ID])

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

def callContract(winner, player1ID, player2ID, tie):
    if (tie):
        args = [b'tie', encoding.decode_address(player1ID)]
    else:
        args = [b'resolve', encoding.decode_address(winner)]

    call_app(my_client, privateKey, publicAdd ,apid, args, player1ID, player2ID)

# [recieve game information]
# check algorand blockchain every few seconds and if any users local state's game 
# ready variable is set to 'true' then pull model id and opponent model id

# Define oracle logic

# Wait for events
def wait_for_events():
    # Initialize the indexer client
    idx_client = indexer.IndexerClient(algod_token, algod_address, headers)
    last_txn_id = 0
    # Loop indefinitely
    while True:
        if gameDone:
            print("Searching for Transactions...")
            # Get the transactions of the smart contract with a higher ID than the last processed ID
            txns = idx_client.search_transactions(
                #address = app_address,
                application_id = apid,
                min_round=last_txn_id + 1
            )

            # Iterate over the new transactions and extract the user ID

            opponents = {}
            botid = {}
            for txn in txns["transactions"]:
                if (txn['tx-type'] == 'appl') and ('local-state-delta' in txn.keys()):
                    local_state = txn['local-state-delta'][0]['delta']
                    for pair in local_state:
                        if base64.b64decode(pair['key']).decode('utf-8') == 'bot': 
                            try: 
                                botid[txn['sender']] = str(int.from_bytes(base64.b64decode(pair['value']['bytes']), 'big'))
                            except:
                                pass
                    if txn['sender'] in opponents:
                        print("running game")
                        runGame(txn['sender'], opponents[txn['sender']], botid[txn['sender']], botid[opponents[txn['sender']]])
                    else:
                        for pair in local_state:
                            if base64.b64decode(pair['key']).decode('utf-8') == 'opponent':
                                try:
                                    opponents[algosdk.encoding.encode_address(base64.b64decode(pair['value']['bytes']))] = txn['sender']
                                except:
                                    pass
                elif ('application-transaction' in txn.keys()):
                    if ('application-args' in txn['application-transaction'].keys()):
                        try:
                            if (base64.b64decode(txn['application-transaction']['application-args'][0])) == b'delete bot':
                                print("deleting bot")
                                deleteBot(str(int.from_bytes(base64.b64decode(txn['application-transaction']['application-args'][1]), 'big')))
                        except:
                            pass
                    # Update the last processed ID
                last_txn_id = max(last_txn_id, txn["confirmed-round"])
        # Wait for a few seconds before checking for new transactions again
        time.sleep(10)

# Main function
def main():
    # Wait for events
    wait_for_events()

if __name__ == "__main__":
    main()
