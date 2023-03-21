import pyteal




def apporve():
    
    
    cleanup = Seq(
        App.localDel(Txn.sender(), Bytes("bet amount")),
        App.localDel(Txn.sender(), Bytes("game outcome")),
        App.localDel(Txn.sender(), Bytes("winner")),
        App.localDel(Txn.sender(), Bytes("bot")),
        
        App.localDel(App.localGet(Txn.sender(), Bytes("opponent")), Bytes("bet amount")),
        App.localDel(App.localGet(Txn.sender(), Bytes("opponent")), Bytes("game outcome")),
        App.localDel(App.localGet(Txn.sender(), Bytes("opponent")), Bytes("winner")),
        App.localDel(App.localGet(Txn.sender(), Bytes("opponent")), Bytes("bot")),
        App.localDel(App.localGet(Txn.sender(), Bytes("opponent")), Bytes("opponent")),
        
        App.localDel(Txn.sender(), Bytes("opponent")),
    )
    
    payout_sender = Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: App.localGet(Txn.sender(), Bytes("bet")) + App.localGet(App.localGet(Txn.sender(), Bytes("opponent")), Bytes("bet")),
            TxnField.receiver: Txn.sender()
        }),
        InnerTxnBuilder.Submit()
    )
    payout_opponent = Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: App.localGet(Txn.sender(), Bytes("bet")) + App.localGet(App.localGet(Txn.sender(), Bytes("opponent")), Bytes("bet")),
            TxnField.receiver: App.localGet(Txn.sender(), Bytes("opponent"))
        }),
        InnerTxnBuilder.Submit()
    )
    
    start_game = Seq(App.localPut(Txn.sender(), Bytes("game outcome"),Int(0)),
        While(App.localGet(Txn.sender(), Bytes("game outcome")) == Int(0)).Do(
            Seq(
                
            )
        ),
        Cond([App.localGet(Txn.sender(), Bytes("winner")) == 1, payout_sender],[True, payout_opponent]),
        cleanup
        )
    
    
    
    #record bet ammount, bot and opponent of sender
    #if the opponent also has the sender as thier opponent start the game else just approve the transaction
    bet = Seq(App.localPut(Txn.sender(), Bytes("bet amount"),Txn.amt),
              App.localPut(Txn.sender(), Bytes("bot"),Txn.applications_args[1]),
               App.localPut(Txn.sender(), Bytes("opponent"),Txn.applications_args[2]),
               Cond([App.localGet(Bytes("opponent"), Bytes("opponent")) == Txn.sender(), start_game], [True, Approve()])
              )
    
    
    
    
    no_op = Cond([Txn.applications_args[0] == Bytes("bet") and Txn.TxType = Bytes("pay"), bet])
    
    return Cond([Txn.on_completion() == "NoOp", no_op])

def clear():
    pass
