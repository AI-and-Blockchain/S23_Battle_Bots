import pyteal
import algosdk
import time

indexer = algosdk.v2client.indexer
last_round = 0
apid = 0
while True:
    transactions = indexer.search_transactions(min_round=last_round+1,address_role="sender",application_id=apid)
    for t in transactions:
        if last_round < t.first_valid_round:#is this right?
            last_round = t.first_valid_round

        if type(t) == type(algosdk.transaction.ApplicationCallTxn) and t.app_args == "bet":
            addr = t.sender
            state = lookup_account_application_local_state(address=addr,application_id=apid,block=t.first_valid_round)
            if state.inbet == "True" and t.app_args == "bet": #fix
                winner = play_game()# need to right this
                if state.betbft != "":
                    params = client.suggested_params()

                params.flat_fee = True
                params.fee = 1000
                app_args = ["resolve", winner]
                txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args,accounts=[state.better,state.opponent])
                signed_txn = txn.sign(private_key)
                tx_id = signed_txn.transaction.get_txid()
                client.send_transactions([signed_txn])
    time.sleep(5)            
    
    