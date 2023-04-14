from pyteal import *
from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk import transaction
from algosdk import encoding
import base64
from bet import approve
from bet import clear
import sys

# create new application
def create_app(
    client: algod.AlgodClient,
    private_key: str,
    approval_program: bytes,
    clear_program: bytes,
    global_schema: transaction.StateSchema,
    local_schema: transaction.StateSchema,
    sender
) -> int:
    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
    )

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # wait for confirmation
    try:
        transaction_response = transaction.wait_for_confirmation(client, tx_id, 5)
        print("TXID: ", tx_id)
        print(
            "Result confirmed in round: {}".format(
                transaction_response["confirmed-round"]
            )
        )
    except Exception as err:
        print(err)
        return 0

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id:", app_id)

    return app_id

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


pr = sys.argv[1]
pu = sys.argv[2]
algod_endpoint = sys.argv[3]
algod_token = sys.argv[4]
purestake_token = {'X-Api-key': algod_token}
my_client = algod.AlgodClient(algod_token, algod_endpoint,headers=purestake_token)

approval_program = compileTeal(approve(),mode=Mode.Application,version=6)
clear_program = compileTeal(clear(),mode=Mode.Application,version=6)

approval_bytes = base64.b64decode(my_client.compile(approval_program)['result'])
clear_bytes = base64.b64decode(my_client.compile(clear_program)['result'])

local_ints = 8
local_bytes = 8
global_ints = 8
global_bytes = 8
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)


apid = create_app(my_client,pr,approval_bytes,clear_bytes,
    global_schema,
    local_schema,
    pu
)
