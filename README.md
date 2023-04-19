# S23_Battle_Bots

## Project Motivation
We are hoping to create a competitive connect4 bot betting circuit. Where users are encouraged to use their computing power and computer science to train intelligent AIs for a chance to win against other competitors.

## User Story
As a computer science major and an avid gambler I want to use my knowledge of AI to train my very own connect4 bot so I can win money by betting on the blockchain.

![image](control_flow.png)

![image](deployment.png)

## Environment Setup
There are four compnents that must be set up in order to get our entire applicaiton to to get our system running.


### 1. Smart Contract

Prerequisites:
* A funded algorans account 
  1. You can generate accounts using betting/accounts.py if you do not have one already
  2. You can fund an account [here](https://testnet.algoexplorer.io/dispenser) 
* An API token like one from [purestake](https://www.purestake.com/)
* algosdk 
* pyteal

To deploy the smart contract run the following command and record the apid it gives you

`python betting/deploy_app.py <your private key> <your public key> <algorand API endpoint> <API token>`

**==NOTE: you may want to modify the local schema in this script to allow players to have more or less bots==**

To to use betting/run.py to interact with the smart contract you must first populate it with some information

1. set your public and private keys to the pu_a and pr_a variables respectively.
2. set your API endpoint to the algod_endpoint variable. 
3. set the apid you recorded previously to the apd variable
4. set the adress of the app to the app_adress variable
  * the app's can be found at https://testnet.algoexplorer.io/application/<apid\>
5. set api token to the algorand_token variable

To interact with the smart contract you can use the following commands

`python betting/run.py opt`
opts your algorand account into the smart contract

`python betting/run.py pay <amount>`
Sends money to the your account in battle bots

`python betting/run.py create`
Creates a bot on your account 

`python betting/run.py delete <bot id>`
Deletes the specified bot from your account

`python betting/run.py transfer <bot id> <address>`
Transfer the specified bot from your account to another account

`python betting/run.py withdrawal <amount>`
Withdrawal the specified amount from the smart contract

`python betting/run.py bet <bot or notbot> <bet amount or bot to stake> <opponent's address> <bot to play with>`

Specifying bot will start a bet in which the staked asset is a bot NFT otherwise the staked asset will be algos



### 2. Oracle

Using the address(es) generated in the previous step populate these variables in oracle.py:
- Algod_token //algod token (can get from https://developer.purestake.io/login)
- Apid //app id from previous step
- App_address //app address from previous step
- privateKey //private key from algorand address for sending winner to contract
- publicAdd  //algorand address for sending winner to contract

Run the oracle in command line: Python3 oracle.py

If this step is successful you can proceed to step 4.

### 3. Q-Learning

The only dependency of q_learning/ is Pytorch. The program was developed with Pytorch version 2.0 and developed with Python 3.10.

That can be installed using pip, `pip install torch`.

The program does NOT need to be called directly for training the battle bots in a game. Other parts of the application call it.

However, `python train.py` explicitly trains the bots.

### 4. Website

In order to get the website component up & running running, the following commands, in order, must be run while in the root folder of our repository

`cd website/src`

`npm install` *(this may take a while)*

`npm run serve`

That's it! Now, your terminal should've provided you with two URLs to visit the working site. If you want to view the site on your own machine, paste the URL that's next to the ***Local*** section into your web browser; if you want to view the site on another machine that's on the same network as the host machine, paste the URL that's next to the ***Network*** section into that computer's web browser.

**== NOTE: Our site was made strictly for 16:9 apsect ratio. The website is neither re-size friendly nor mobile-friendly. ==**
