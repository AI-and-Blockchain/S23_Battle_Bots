from pyteal import *
from algosdk.v2client import algod
from algosdk import account, mnemonic
from algosdk import transaction
import base64



def approve():
    
    opp = ScratchVar(TealType.bytes)
    cleanup = Seq(
        App.localDel(Txn.application_args[1], Bytes("bet amount")),
        App.localPut(Txn.application_args[1], Bytes("bet ready"),Bytes("N/A")),
        App.localPut(Txn.application_args[1], Bytes("bot"),Bytes("N/A")),
        App.localPut(Txn.application_args[1], Bytes("bot staked"),Bytes("N/A")),
        
        App.localDel(App.localGet(Txn.application_args[1], Bytes("opponent")), Bytes("bet amount")),
        App.localPut(App.localGet(Txn.application_args[1], Bytes("opponent")), Bytes("bet ready"), Bytes("N/A")),
        App.localPut(App.localGet(Txn.application_args[1], Bytes("opponent")), Bytes("bot"),Bytes("N/A")),
        App.localPut(App.localGet(Txn.application_args[1], Bytes("opponent")), Bytes("bot staked"),Bytes("N/A")),
        App.localDel(App.localGet(Txn.application_args[1], Bytes("opponent")), Bytes("opponent")),
        
        App.localDel(Txn.application_args[1], Bytes("opponent")),
    )
    
    payout = Seq(opp.store(App.localGet(Txn.application_args[1], Bytes("opponent"))),
        Cond([App.localGet(opp.load(),Bytes("bot staked")) == Bytes("N/A"),
        Seq(
            App.localPut(Txn.application_args[1],Bytes("balance"),App.localGet(Txn.application_args[1],Bytes("balance"))+ App.localGet(opp.load(), Bytes("bet"))),
            App.localPut(opp.load(),Bytes("balance"),App.localGet(opp.load(),Bytes("balance")) - App.localGet(opp.load(), Bytes("bet"))),
        )
        ],
        [App.localGet(opp.load(),Bytes("bot staked")) != Bytes("N/A"),
         Seq(App.localPut(Txn.application_args[1],App.localGet(opp.load(),(Bytes("bot"))),Int(1)),
         App.localDel(opp.load(),App.localGet(opp.load(),(Bytes("bot")))))]
        ),
        cleanup
    )


    check_bet_status = If(App.localGet(Txn.sender(),Bytes("bet ready")) == Bytes("N/A")
                ).Then(Seq(App.localPut(Txn.sender(),Bytes("bet ready"),Bytes("false")),App.localPut(Txn.application_args[3],Bytes("bet ready"),Bytes("false")))
                ).ElseIf(App.localGet(Txn.sender(),Bytes("bet ready")) == Bytes("false")
                ).Then(Seq(App.localPut(Txn.sender(),Bytes("bet ready"),Bytes("true")),App.localPut(Txn.application_args[3],Bytes("bet ready"),Bytes("true")))
                ).Else(Return(Int(0)))    

    #record bet ammount, bot and opponent of sender
    #if the opponent also has the sender as thier opponent start the game else just approve the transaction
    bet = If(Txn.application_args[1] != Bytes("bot")
    ).Then(
        If(And(App.localGet(Txn.sender(),Bytes("balance")) >= Btoi(Txn.application_args[2]),App.localGet(Txn.sender(),Txn.application_args[4]) == Int(1))
        ).Then(Seq(
                App.localPut(Txn.sender(), Bytes("bet amount"),Btoi(Txn.application_args[2])),
                App.localPut(Txn.sender(), Bytes("opponent"),Txn.application_args[3]),
                App.localPut(Txn.sender(), Bytes("bot"),Txn.application_args[4]), #this is the bot id 
                check_bet_status         
              )
        ).Else(Return(Int(0))) 
    ).ElseIf(And(Txn.application_args[1] == Bytes("bot"),App.localGet(Txn.sender(),Txn.application_args[4]) == Int(1),App.localGet(Txn.sender(),Txn.application_args[2]) == Int(1))
    ).Then(Seq(
                App.localPut(Txn.sender(), Bytes("bot staked"),Txn.application_args[2]),
                App.localPut(Txn.sender(), Bytes("opponent"),Txn.application_args[3]),
                App.localPut(Txn.sender(), Bytes("bot"),Txn.application_args[4]), 
                check_bet_status
            )
    ).Else(Return(Int(0)))
    
    
    
    
 
   
    
    process_payment = Seq(App.localPut(Gtxn[0].sender(),Bytes("balance"),App.localGet(Gtxn[0].sender(),Bytes("balance"))+Gtxn[0].amount()))
    
    withdrawal = Cond([App.localGet(Txn.sender(),Bytes("balance")) >= Btoi(Txn.application_args[1]),
                        Seq(
                                App.localPut(Txn.sender(),Bytes("balance"),App.localGet(Txn.sender(),Bytes("balance"))-Btoi(Txn.application_args[1])),
                                InnerTxnBuilder.Begin(),
                                InnerTxnBuilder.SetFields({
                                    TxnField.type_enum: TxnType.Payment,
                                    TxnField.receiver: Txn.sender(),
                                    TxnField.amount: Btoi(Txn.application_args[1])
                                }),
                                InnerTxnBuilder.Submit()
                            )
                    ])
                        
    create_bot = Seq(
                        App.localPut(Txn.sender(),Itob(App.globalGet((Bytes("num bots")))),Int(1)),
                        App.globalPut(Bytes("num bots"),App.globalGet((Bytes("num bots")))+Int(1))
                    )
    
    
    
    optin = Seq(
                App.localPut(Txn.sender(),Bytes("balance"),Int(0)),
                App.localPut(Txn.sender(),Bytes("bet ready"),Bytes("N/A")),
                App.localPut(Txn.sender(),Bytes("bot"),Bytes("N/A")),
                App.localPut(Txn.sender(),Bytes("bot staked"),Bytes("N/A")),
                )
    
    setup = App.globalPut(Bytes("num bots"),Int(0))
    
    delete_bot = App.localDel(Txn.sender(),Txn.application_args[1])
    
    transfer_bot = Seq(
                        App.localPut(Txn.application_args[2],Txn.application_args[1],Int(1)),
                        App.localDel(Txn.sender(),Txn.application_args[1]),
                       )
    
    check_global_txn = And(Gtxn[0].type_enum() == TxnType.Payment,
                           Gtxn[0].receiver() == Global.current_application_address())
    
    
    no_op = If(And(Global.group_size() > Int(1),Txn.application_args[0] == Bytes("pay"))
        ).Then(
            If(check_global_txn)
            .Then(process_payment)
            .Else(Return(Int(0)))
    ).ElseIf(And(Txn.application_args[0] == Bytes("bet"),App.localGet(Txn.sender(),Bytes("bet ready")) != Bytes("true"))
    ).Then(bet
    ).ElseIf(Txn.application_args[0] == Bytes("withdrawal")
    ).Then(withdrawal
    ).ElseIf(Txn.application_args[0] == Bytes("resolve")
    ).Then(payout
    ).ElseIf(Txn.application_args[0] == Bytes("tie")
    ).Then(cleanup
    ).ElseIf(Txn.application_args[0] == Bytes("create bot")
    ).Then(create_bot
    ).ElseIf(And(Txn.application_args[0] == Bytes("transfer bot"),App.localGet(Txn.sender(),Bytes("bot")) != Txn.application_args[1],App.localGet(Txn.sender(),Bytes("bot staked")) != Txn.application_args[1])
    ).Then(transfer_bot
    ).ElseIf(And(Txn.application_args[0] == Bytes("delete bot"),App.localGet(Txn.sender(),Bytes("bot")) != Txn.application_args[1],App.localGet(Txn.sender(),Bytes("bot staked")) != Txn.application_args[1])
    ).Then(delete_bot
    ).Else(App.globalPut(Bytes("bonk"), Bytes("bonk")))
    
    return Seq(Cond([Txn.application_id() == Int(0), setup],
                [Txn.on_completion() == OnComplete.OptIn, optin],
                [Int(1) == Int(1), no_op]
                ),Return(Int(1)))

def clear():
    return Return(Int(1))
