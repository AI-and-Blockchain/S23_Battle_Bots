import algosdk

# dispenser: https://testnet.algoexplorer.io/dispenser

private_key, account_address = algosdk.account.generate_account()
mnemonic = algosdk.mnemonic.from_private_key(private_key)
account1 = {"private_key" : private_key, "account_address" : account_address, "mnemonic" : mnemonic}

private_key, account_address = algosdk.account.generate_account()
mnemonic = algosdk.mnemonic.from_private_key(private_key)
account2 = {"private_key" : private_key, "account_address" : account_address, "mnemonic" : mnemonic}

print("private_key: ", account1["private_key"])
print("account_address: ", account1["account_address"])
print("mnemonic: ", account1["mnemonic"])

print("private_key: ", account2["private_key"])
print("account_address: ", account2["account_address"])
print("mnemonic: ", account2["mnemonic"])


