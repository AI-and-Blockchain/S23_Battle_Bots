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
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args,accounts=["AHHCIFLRPIBH7RA3JFQUTZNIWGBRDRU2UGDLIHGIVVBE3R66LMRI3S2V2I","XFVEXFPLMZOJFDZS7Y5CFXISSSI6J5P4RVMTJPRLIUQ2YI5NH74LTH3RCU"]) # Put Adds here

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

def gp(client, private_key, pub,index, app_args):
    # declare sender
    sender = pub
    print("Call from account:", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args,accounts=["XFVEXFPLMZOJFDZS7Y5CFXISSSI6J5P4RVMTJPRLIUQ2YI5NH74LTH3RCU","AHHCIFLRPIBH7RA3JFQUTZNIWGBRDRU2UGDLIHGIVVBE3R66LMRI3S2V2I"]) # Put Adds here

    return txn

    # sign transaction
    # signed_txn = txn.sign(private_key)
    # tx_id = signed_txn.transaction.get_txid()

    # # send transaction
    # client.send_transactions([signed_txn])

    # # await confirmation
    # wait_for_confirmation(client, tx_id)



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
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args,accounts=["XFVEXFPLMZOJFDZS7Y5CFXISSSI6J5P4RVMTJPRLIUQ2YI5NH74LTH3RCU","AHHCIFLRPIBH7RA3JFQUTZNIWGBRDRU2UGDLIHGIVVBE3R66LMRI3S2V2I"]) # Put Adds here

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


pr_a = "L4I6lbi8S/Nr86UDno66qK5reFegnTqOqZyIkZGOr4S5akuV62Zcko8y/joi3RKUkeT1/I1ZNL4rRSGsI60/+A=="
pr_b = "YYM6VSn6UPsXRHdYNTqfSHDNn6MuNY1X3Pt9bL7iJAsBziQVcXoCf8QbSWFJ5aixgxHGmqGGtBzIrUJNx95bIg=="
pu_a = "XFVEXFPLMZOJFDZS7Y5CFXISSSI6J5P4RVMTJPRLIUQ2YI5NH74LTH3RCU"
pu_b = "AHHCIFLRPIBH7RA3JFQUTZNIWGBRDRU2UGDLIHGIVVBE3R66LMRI3S2V2I"
pa = encoding.decode_address(pu_a)
pb = encoding.decode_address(pu_b)

# opt_in_app(client, private_key, pub, index)

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "1sAOEAI4mA8zfmlrSg5K51xB3ryOkYAl4BJIL8zU" # PUT TOKEN HERE
headers = {"X-API-KEY": algod_token}
my_client = algod.AlgodClient(algod_token, algod_address, headers)

apid = 194432039 # PUT APP ID HERE
app_address = "VUECXHLFX4QXVT5GFVOLZ27YSIOEN5BFJQXLF4VU357FVOAGFRBAX3CIIM" # PUT APP ADDRESS HERE

# opt_in_app(my_client, pr_a,pu_a, apid)
# opt_in_app(my_client, pr_b,pu_b, apid)
params = my_client.suggested_params()


amount = 100000

args = [b'pay']
send_balance(my_client, pr_a, pu_a,apid, args,app_address)
send_balance(my_client, pr_b, pu_b,apid, args,app_address)
print("sent money")

args = [b'create bot']
call_app(my_client, pr_a,pu_a, apid, args)
call_app(my_client, pr_b, pu_b, apid, args)
print("bots made")

# i = 1
# args = [b'withdrawal',i.to_bytes(8, 'big')]
# call_app(my_client, pr_a, pu_a, apid, args)
# print("withdraw pass")

i = 5
k = 0
args = [b'bet',b'not bot',i.to_bytes(8, 'big'), pb,k.to_bytes(8, 'big')]
at =  gp(my_client, pr_a, pu_a,apid, args)
i = 5
k = 1
args = [b'bet',b'not bot',i.to_bytes(8, 'big'),pa,k.to_bytes(8, 'big')]
bt = gp(my_client, pr_b, pu_b,apid, args)
transaction.assign_group_id([at, bt])
sat = at.sign(pr_a)
tx_id = sat.get_txid()
bat = bt.sign(pr_b)
signed_group = [sat, bat]

my_client.send_transactions(signed_group)
wait_for_confirmation(my_client, tx_id)


print("bet passed")
