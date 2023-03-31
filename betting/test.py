from pyteal import *
from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk import transaction
from algosdk import encoding
import base64
from bet import apporve
from bet import clear


# create new application
def create_app(
    client: algod.AlgodClient,
    private_key: str,
    approval_program: bytes,
    clear_program: bytes,
    global_schema: transaction.StateSchema,
    local_schema: transaction.StateSchema,
) -> int:
    # define sender as creator
    sender = account.address_from_private_key(private_key)

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

def opt_in_app(client, private_key, index):
    # declare sender
    sender = account.address_from_private_key(private_key)
    print("OptIn from account: ", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationOptInTxn(sender, params, index)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("OptIn to app-id:", transaction_response["txn"]["txn"]["apid"])
    





def call_app(client, private_key, index, app_args):
    # declare sender
    sender = account.address_from_private_key(private_key)
    print("Call from account:", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args,accounts=[pu_a,pu_b,pu_c])

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

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


create_app(my_client,pr_a,approval_bytes,clear_bytes,
    global_schema,
    local_schema,
)

purestake_token = {'X-Api-key': ""}
pr_a = ""
pu_a = ""
pr_b = ""
pu_b = ""
pr_c = ""
pu_c = ""
my_client = algod.AlgodClient("","https://testnet-algorand.api.purestake.io/ps2",headers=purestake_token)

apid = 0

opt_in_app(my_client, pr_a, apid)

app_adress = ""

params = my_client.suggested_params()

app_adress = ""
amount = 5

unsigned_transaction = transaction.PaymentTxn(pu_a, params, app_adress, amount, None)

signed_transaction = unsigned_transaction.sign(pr_a)

txid = my_client.send_transaction(signed_transaction)

wait_for_confirmation(my_client, tx_id)

opt_in_app(my_client, pr_b, apid)

unsigned_transaction = transaction.PaymentTxn(pu_b, params, app_adress, amount, None)

signed_transaction = unsigned_transaction.sign(pr_b)

txid = my_client.send_transaction(signed_transaction)

wait_for_confirmation(my_client, tx_id)

args = [b'create bot']

call_app(my_client, pr_a, apid, args)

call_app(my_client, pr_b, apid, args)

i = 1
args = [b'withdrawal',i.to_bytes(8, 'big')]

call_app(my_client, pr_a, apid, args)

args = [b'bet',i.to_bytes(8, 'big')]

call_app(my_client, pr_a, apid, args)

call_app(my_client, pr_b, apid, args)

i = 0
pb = encoding.decode_address(pu_b)
args = [b'tranfer bot',i.to_bytes(8, 'big'),pb]

call_app(my_client, pr_a, apid, args)

i = 0
args = [b'delete bot',i.to_bytes(8, 'big')]

call_app(my_client, pr_b, apid, args)
