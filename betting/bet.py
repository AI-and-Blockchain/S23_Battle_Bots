import pyteal




def apporve():
    
    
    cleanup = Seq(
        App.localDel(Txn.applications_args[1], Bytes("bet amount")),
        App.localPut(Txn.applications_args[1], Bytes("bet ready"),Bytes("N/A")),
        App.localPut(Txn.applications_args[1], Bytes("bot"),Bytes("N/A")),
        App.localDel(Txn.applications_args[1], Bytes("bet bot")),
        
        App.localDel(App.localGet(Txn.applications_args[1], Bytes("opponent")), Bytes("bet amount")),
        App.localPut(App.localGet(Txn.applications_args[1], Bytes("opponent")), Bytes("bet ready"), Bytes("N/A")),
        App.localPut(App.localGet(Txn.applications_args[1], Bytes("opponent")), Bytes("bot"),Bytes("N/A")),
        App.localDel(App.localGet(Txn.applications_args[1], Bytes("opponent")), Bytes("bet bot")),
        App.localDel(App.localGet(Txn.applications_args[1], Bytes("opponent")), Bytes("opponent")),
        
        App.localDel(Txn.applications_args[1], Bytes("opponent")),
    )
    
    payout = Seq(opp.store(App.localGet(Txn.applications_args[1], Bytes("opponent"))),
        Cond([App.localGet(opp.load(),Bytes("bet bot")) == Int(0),
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: App.localGet(Txn.sender(), Bytes("bet")) + App.localGet(App.localGet(Txn.sender(), Bytes("opponent")), Bytes("bet")),
            TxnField.receiver: Txn.applications_args[1]
        }),
        InnerTxnBuilder.Submit()],
        [App.localGet(App.localGet(Txn.applications_args[1], Bytes("opponent")),Bytes("bet bot")) == Int(1),
         App.localPut(Txn.applications_args[1],App.localGet(opp.load(),(Bytes("bot"))),Int(1)),
         App.localDel(opp.load(),App.localGet(opp.load(),(Bytes("bot"))))]
        ),
        cleanup
    )

    #record bet ammount, bot and opponent of sender
    #if the opponent also has the sender as thier opponent start the game else just approve the transaction
    bet = Cond([Txn.applications_args[2] != Bytes("bot"),Cond([App.localGet(Txn.sender(),Bytes("balance")) >= Btoi(Txn.applications_args[2]),
                Seq(
                    App.localPut(Txn.sender(), Bytes("bet bot"),Int(0)),
                    App.localPut(Txn.sender(), Bytes("bet amount"),Btoi(Txn.applications_args[2])),
                    App.localPut(Txn.sender(), Bytes("opponent"),Txn.applications_args[3]),
                    Cond([App.localGet(Txn.sender(),Txn.applications_args[4]) == Int(1),App.localPut(Txn.sender(), Bytes("bot"),Txn.applications_args[4])]),
                    Cond([App.localGet(Txn.sender(),Bytes("bet ready")) == Bytes("N/A"),#fix for malicous bets
                          Seq(App.localPut(Txn.sender(),Bytes("bet ready"),Bytes("false")),App.localPut(Txn.applications_args[3],Bytes("bet ready"),Bytes("false")))],              
                          [App.localGet(Txn.sender(),Bytes("bet ready")) == Bytes("false"),  
                            Seq(App.localPut(Txn.sender(),Bytes("bet ready"),Bytes("true")),App.localPut(Txn.applications_args[3],Bytes("bet ready"),Bytes("true")))])                       
                )
                
                ])],[Txn.applications_args[2] == Bytes("bot"), 
                    Seq(
                        App.localPut(Txn.sender(), Bytes("bet bot"),Int(1)),
                        App.localPut(Txn.sender(), Bytes("opponent"),Txn.applications_args[3]),
                        Cond([App.localGet(Txn.sender(),Txn.applications_args[4]) == Int(1),App.localPut(Txn.sender(), Bytes("bot"),Txn.applications_args[4])]), 
                        Cond([App.localGet(Txn.sender(),Bytes("bet ready")) == Bytes("N/A"),#fix for malicous bets
                          Seq(App.localPut(Txn.sender(),Bytes("bet ready"),Bytes("false")),App.localPut(Txn.applications_args[3],Bytes("bet ready"),Bytes("false")))],              
                          [App.localGet(Txn.sender(),Bytes("bet ready")) == Bytes("false"),  
                            Seq(App.localPut(Txn.sender(),Bytes("bet ready"),Bytes("true")),App.localPut(Txn.applications_args[3],Bytes("bet ready"),Bytes("true")))])
                    ) 
                    ]
            )
    
    process_payment = App.localPut(Txn.sender(),Bytes("balance"),App.localGet(Txn.sender(),Bytes("balance"))+Txn.amt)
    
    withdrawal = Cond([App.localGet(Txn.sender(),Bytes("balance")) >= Btoi(Txn.applications_args[1]),
                        Seq(
                                App.localPut(Txn.sender(),Bytes("balance"),App.localGet(Txn.sender(),Bytes("balance"))-Txn.applications_args[1]),
                                InnerTxnBuilder.Begin(),
                                InnerTxnBuilder.SetFields({
                                    TxnField.type_enum: TxnType.Payment,
                                    TxnField.receiver: Txn.sender(),
                                    TxnField.amount: Txn.applications_args[1]
                                }),
                                InnerTxnBuilder.Submit()
                            )
                    ])
                        
    create_bot = Seq(
                        App.localPut(Txn.sender(),App.globalGet((Bytes("num bots"))),Int(1)),
                        App.globalPut((Bytes("num bots"),App.globalGet((Bytes("num bots")))+Int(1)))
                    )
    
    
    
    optin = Seq(
                App.localPut(Txn.sender(),Bytes("balance"),Int(0)),
                App.localPut(Txn.sender(),Bytes("bet ready"),Bytes("N/A")),
                App.localPut(Txn.sender(),Bytes("bot"),Bytes("N/A")),
                )
    
    no_op = Cond([Txn.type == Bytes("pay"),process_payment],
                 [Txn.applications_args[0] == Bytes("bet")and 
                  App.localGet(Txn.sender(),Bytes("bet ready")) == Bytes("N/A"), bet],
                 [Txn.applications_args[0] == Bytes("withdrawal"), withdrawal],
                 [Txn.applications_args[0] == Bytes("resolve"), payout],
                 [Txn.applications_args[0] == Bytes("create bot"),create_bot],
                 [Txn.applications_args[0] == Bytes("transfer bot") and 
                  App.localGet(Txn.sender(),Bytes("bot")) != Txn.applications_args[1],transfer_bot],
                 [Txn.applications_args[0] == Bytes("delete bot") and 
                  App.localGet(Txn.sender(),Bytes("bot")) != Txn.applications_args[1],delete_bot],
                 )
    
    setup = App.globalPut(Bytes("num bots"),Int(0))
    
    delete_bot = App.localDel(Txn.sender(),Txn.applications_args[1])
    
    transfer_bot = Seq(
                        App.localPut(Txn.applications_args[2],Txn.applications_args[1],Int(1)),
                        App.localDel(Txn.sender(),Txn.applications_args[1]),
                       )
    
    return Cond([Txn.application_id() == Int(0), setup],[Txn.on_completion() == "NoOp", no_op],[Txn.on_completion() == "Optin", optin])

def clear():
    Return(1)
