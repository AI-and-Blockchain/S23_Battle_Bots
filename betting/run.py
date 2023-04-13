from pyteal import *
from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk import transaction
from algosdk import encoding
import base64

def send_balance(client, private_key, pub,index, app_args,app_adress,amt):
    # declare sender
    sender = pub
    print("Call from account:", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000
    amount = amt
    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args,accounts=[sys.argv[2],sys.argv[3]])

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





def call_app(client, private_key, pub,index, app_args,account_list):
    # declare sender
    sender = pub
    print("Call from account:", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args,accounts=account_list)

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


pr_a = ""
pu_a = ""
pa = encoding.decode_address(pu_a)


 

algod_address = ""
algod_token = ""
purestake_token = {'X-Api-key': algod_token}
my_client = algod.AlgodClient(algod_token, algod_address,headers=purestake_token)

apid = ""
app_adress = ""

if sys.argv[2] == "pay":
   args = [b'pay'] 
   amount = stoi(sys.argv[3])
   send_balance(my_client, pr_a, pu_a,apid, args,app_adress,amount)
   print("sent money")
elif sys.argv[2] == "create":
    args = [b'create bot']
    call_app(my_client, pr_a,pu_a, apid, args,account_list)
    print("bot made")
elif sys.argv[2] == "withdrawal":
    i = int(sys.argv[3])
    args = [b'withdrawal',i.to_bytes(8, 'big')]
    call_app(my_client, pr_a, pu_a, apid, args,account_list)
    print("money withdrawaled")
elif sys.argv[2] == "transfer":
    i = int(sys.argv[3])
    pb = encoding.decode_address(sys.argv[4])
    args = [b'transfer bot',i.to_bytes(8, 'big'),pb]
    account_list = [pu_a,sys.argv[4]]
    call_app(my_client, pr_a, pu_a,apid, args,account_list)
    print("bot transfered")
elif sys.argv[2] == "delete":
    i = int(sys.argv[3])
    args = [b'delete bot',i.to_bytes(8, 'big')]
    call_app(my_client, pr_b, pu_b,apid, args,account_list)
    print("bot deleted")
elif sys.argv[2] == "bet" and sys.argv[3] == "bot":
    bet_amount = int(sys.argv[4])
    oppnent = sys.argv[5]
    pb = encoding.decode_address(sys.argv[6])
    botid = int(sys.argv[7])
    account_list = [pu_a,sys.argv[6]]
    args = [b'bet',b'bot',bet_amount.to_bytes(8, 'big'), pb,botid.to_bytes(8, 'big')]
    call_app(my_client, pr_a, pu_a,apid, args,account_list)
    print("bet made")
elif sys.argv[2] == "bet" and sys.argv[5] == "not bot":
    bet_amount = int(sys.argv[6])
    botid = int(sys.argv[7])
    args = [b'bet',b'not bot',bet_amount.to_bytes(8, 'big'), pb,botid.to_bytes(8, 'big')]
    call_app(my_client, pr_a, pu_a,apid, args,account_list)
    print("bet made")


