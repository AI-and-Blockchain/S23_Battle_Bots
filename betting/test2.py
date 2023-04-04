from pyteal import *
from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk import transaction
from algosdk import encoding
import base64

def send_balance(client, private_key, pub,index, app_args,app_adress):
    # declare sender
    sender = pub
    print("Call from account:", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000
    amount = 100000
    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args,accounts=["",""])

    unsigned_transaction = transaction.PaymentTxn(sender, params, app_adress, amount, None)

    transaction.assign_group_id([unsigned_transaction, txn])
    
    
    signed_transaction = unsigned_transaction.sign(private_key)
    
    # sign transaction
    signed_txn = txn.sign(private_key)
    
    signed_group = [signed_transaction, signed_txn]
    
    
    
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions(signed_group)

    # await confirmation
    wait_for_confirmation(client, tx_id)





def call_app(client, private_key, pub,index, app_args):
    # declare sender
    sender = pub
    print("Call from account:", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args,accounts=["",""])

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

def opt_in_app(client, private_key, pub, index):
    # declare sender
    sender = pub
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


pr_a = mnemonic.to_master_derivation_key("")
pr_b = mnemonic.to_master_derivation_key("")
pu_a = ""
pu_b = ""
pa = encoding.decode_address(pu_a)
pb = encoding.decode_address(pu_b)



algod_address = "http://localhost:4001"
algod_token = "a" * 64
my_client = algod.AlgodClient(algod_token, algod_address)

apid = 475
app_adress = ""
# opt_in_app(my_client, pr_a,pu_a, apid)

params = my_client.suggested_params()


amount = 100000

args = [b'pay']
send_balance(my_client, pr_a, pu_a,apid, args,app_adress)
send_balance(my_client, pr_b, pu_b,apid, args,app_adress)
print("sent moeny")

args = [b'create bot']

call_app(my_client, pr_a,pu_a, apid, args)

call_app(my_client, pr_b, pu_b, apid, args)
print("bots made")
i = 1
args = [b'withdrawal',i.to_bytes(8, 'big')]

call_app(my_client, pr_a, pu_a, apid, args)

print("withdraw pass")

i = 5
k = 0
args = [b'bet',b'not bot',i.to_bytes(8, 'big'), pb,k.to_bytes(8, 'big')]

call_app(my_client, pr_a, pu_a,apid, args)

i = 5
k = 1
args = [b'bet',b'not bot',i.to_bytes(8, 'big'),pa,k.to_bytes(8, 'big')]

call_app(my_client, pr_b, pu_b,apid, args)

print("bet passed")


args = [b'resolve',pa]

call_app(my_client, pr_b, pu_b,apid, args)


print("bet resloved")

i = 0
pb = encoding.decode_address(pu_b)
args = [b'transfer bot',i.to_bytes(8, 'big'),pb]

call_app(my_client, pr_a, pu_a,apid, args)
print("transfer passed")
i = 0

args = [b'delete bot',i.to_bytes(8, 'big')]

call_app(my_client, pr_b, pu_b,apid, args)

print("delete passed")
