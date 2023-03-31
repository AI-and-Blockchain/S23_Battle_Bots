from algosdk import account, encoding, mnemonic
from algosdk.future.transaction import Transaction
from algosdk.v2client import algod
from algosdk.v2client.models import DryrunSource, DryrunRequest, DryrunResponse
from algosdk.wallet import Wallet
from pyteal import *
from q_learning.train import play_battle_bots
from model import MyMongoDB
import time
import os

# reference
# https://github.com/AI-and-Blockchain/S23_PredictChain/blob/main/oracle/oracleCore.py
# for oracle outline/ syntax

"""
1) Set up an Algorand node: To interact with the Algorand blockchain, 
you will need to run an Algorand node. You can set up a node on your 
local machine or use a cloud provider such as AWS, Azure, or Google Cloud.

2) Connect to the Algorand node: Once you have set up an Algorand node, 
you can connect to it using the Algorand SDK in Python. You will need to 
specify the address and port of the node, as well as your Algorand account 
credentials.

3) Deploy your smart contract: You will need to deploy your smart contract 
on the Algorand blockchain using a tool such as PyTeal, which allows you to 
write and compile Algorand smart contracts in Python.

4) Define your oracle: Your oracle will need to be written in Python and 
hosted on a server or cloud provider. It should listen for events related to 
your smart contract on the Algorand blockchain and perform actions based on 
those events.

5) Set up a data source: Your oracle will need a data source that it can use 
to determine whether certain conditions have been met on the blockchain. This 
could be a web API, a database, or another external source of data.

6) Define your oracle logic: Your oracle logic should specify what actions your 
oracle should take based on the data it receives from the data source. For 
example, if a certain condition is met on the blockchain, your oracle might 
update a database, trigger a webhook, or send a notification to a user.

7) Register your oracle: Once you have defined your oracle and its logic, you 
will need to register it with the Algorand blockchain using a smart contract. 
This will allow your oracle to receive notifications when events related to your 
smart contract occur on the blockchain.

8) Run your oracle: Finally, you can run your oracle and monitor the Algorand 
blockchain for changes related to your smart contract. Your oracle should be set 
up to listen for events and trigger actions based on the logic you have defined.

"""

# Connect to Algorand node
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = {"X-API-Key": "<YOUR API KEY>"}
algod_client = algod.AlgodClient(algod_token, algod_address)

# Define smart contract information
program = b"<SMART CONTRACT ADDRESS HERE>"


# [run game]
# pull model from MongloDB database in model.py and call play_battle_bots in train.py

def runGame(player1ID, player2ID):
    # get player models
    player1 = getModel(player1ID)
    player2 = getModel(player2ID)
    # play game
    player1, player2, actions, winner = play_battle_bots(player1, player2)
    updateDatabase(player1ID, player1, player2ID, player2)
    updateWebsite(actions, winner)
    callContract(winner)


def getModel(playerID):
    # pull model from MongoDB database
    print("Not Implemented")


# [update and send info]
# with the return from play_battle_bots update models in database, update 
# website with moves, and call smart contract with winner (with word 'resolve'
# as first arguement), winner id must be base32 encoded.
# Connect to Algorand node
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = {"X-API-Key": "<YOUR API KEY>"}
algod_client = algod.AlgodClient(algod_token, algod_address)

# Define smart contract information
program = b"<SMART CONTRACT ADDRESS HERE>"
def updateDatabase(player1ID, player1Model, player2ID, player2Model):
    # send models to MongoDB database
    print("Not Implemented")

def updateWebsite(actions, winner):
    # send moves and winner to website
    print("Not Implemented")

def callContract(winner):
    # send winner to smart contract

    # Define the parameters for the transaction
    params = algod_client.suggested_params()
    params.fee = 1000
    params.flat_fee = True

    # Define the arguments for the transaction
    arguments = ["resolve".encode(), winner.encode()]


    # Build the transaction
    txn = Transaction(
        sender=algod_address,
        sp=params,
        app_id=program,
        on_complete=OnComplete.NoOpOC.real,
        note=bytes("Winner of the bet".encode()),
        app_args=arguments,
    )

    # Sign the transaction
    signed_txn = txn.sign(algod_token)

    # Send the transaction
    tx_id = algod_client.send_transaction(signed_txn)
    print(f"Transaction ID: {tx_id}")



# [recieve game information]
# check algorand blockchain every few seconds and if any users local state's game 
# ready variable is set to 'true' then pull model id and opponent model id

# Define oracle logic
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


# Wait for events
def wait_for_events():
    # Subscribe to events
    event_listener = algod_client.events()
    event_listener.state(delta=1, application_id=program).subscribe(process_event)

    # Keep the script running
    while True:
        time.sleep(1)

# Main function
def main():
    # Wait for events
    wait_for_events()

if __name__ == "__main__":
    main()
