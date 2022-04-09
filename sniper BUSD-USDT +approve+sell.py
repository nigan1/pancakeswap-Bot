# import the following dependencies
import json
from web3 import Web3
import asyncio
import config
import time


# add your blockchain connection information
bsc = 'https://bsc-dataseed.binance.org/'    
web3 = Web3(Web3.HTTPProvider(bsc))

if web3.isConnected():
    print(f'Conectado a BSC Mainnet')
else:
    print(f'Falla en conectar a BSC Mainnet, intente de nuevo.')
    quit()

# uniswap factory address and abi = pancakeswap factory
pancake_factory = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'  #Testnet  #0x6725F303b657a9451d8BA641348b6761A6CC7a17
pancake_factory_abi = json.loads(config.pancake_factory)

contract = web3.eth.contract(address=pancake_factory, abi=pancake_factory_abi)

#abi to sell
sellAbi = (config.sellAbi)

#pancakeswap router abi 
panRouterContractAddress = '0x10ED43C718714eb63d5aA57B78B54704E256024E'    

panabi = config.panabi

contractbuy = web3.eth.contract(address=panRouterContractAddress, abi=panabi)

tokenValue= web3.toWei(config.inversion, 'ether')

spend = web3.toChecksumAddress(config.busd)   #bust/usdt token con que tenga liquidez el token que vas a comprar

sender_address = web3.toChecksumAddress(config.wallet_bsc) 

tokenToBuy = web3.toChecksumAddress(input("Contrato del token a comprar: "))

#Si las condiciones se cumplen se compra

def buy():
	pancakeswap2_txn = contract.functions.swapExactTokensForTokens(
            tokenValue,0, 
            [spend, tokenToBuy],
            sender_address,
            (int(time.time()) + 1000000)

            ).buildTransaction({
            'from': sender_address,
            'gasPrice': web3.toWei(config.gas,'gwei'),
            'nonce': web3.eth.get_transaction_count(sender_address),
            })

	signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=config.private_key)
	tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
	print('Transaccion completada!!')
	print('Hash de transaccion: ', web3.toHex(tx_token))



def info_check():
    contractApprove = web3.toChecksumAddress(tokenToBuy)

    abiToCheck = [
        {
            "constant": True,
            "inputs": [
                {"name": "_owner", "type": "address"},
                {"name": "_spender", "type": "address"},
            ],
            "name": "allowance",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function",
        },
    ]

    contractApprove = web3.eth.contract(address=contractApprove, abi=abiToCheck)


    _owner = web3.toChecksumAddress(config.wallet_bsc) #wallet de usuario
    _spender = web3.toChecksumAddress(panRouterContractAddress) #router de pancakeswap, que es donde apruebo el token para venderlo ahi

    allowToSell = contractApprove.functions.allowance(_owner, _spender).call()

    print(" ")

    if allowToSell<1:
        print("el token que ha comprado no esta aprobado para su venta")
    else:
        print("el token que ha comprado ya le tenia aprobado para su venta")


    #checar token comprados y calcular precio promedio de compra
    token_comprados=0

    while token_comprados==0:
        sellTokenContract = web3.eth.contract(tokenToBuy, abi=sellAbi)
        balance_token = sellTokenContract.functions.balanceOf(sender_address).call()
        symbol = sellTokenContract.functions.symbol().call()
        readable = web3.fromWei(balance_token,'ether')
        token_comprados+=readable

    print("Has comprado " + str(readable) + " " + symbol)
    print("A un precio promedio de "+str(config.inversion/readable))

    print(" ")

    #Approve Token before Selling
    if allowToSell<1:
        print("aprobando token...")

        approve = sellTokenContract.functions.approve(panRouterContractAddress, balance_token).buildTransaction({
                    'from': sender_address,
                    'gasPrice': web3.toWei(config.gas_approve,'gwei'),
                    'nonce': web3.eth.get_transaction_count(sender_address),
                    })

        signed_txn = web3.eth.account.sign_transaction(approve, private_key=config.private_key)
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print("venta del token aprobada")
        print("Approved: " + web3.toHex(tx_token))


def sell():

    sellTokenContract = web3.eth.contract(tokenToBuy, abi=sellAbi)
    balance_token = sellTokenContract.functions.balanceOf(sender_address).call()

    pancakeswap3_txn = contract.functions.swapExactTokensForTokens(
            balance_token,0, 
            [tokenToBuy, spend],
            sender_address,
            (int(time.time()) + 1000000)

            ).buildTransaction({
            'from': sender_address,
            'gasPrice': web3.toWei(config.gas,'gwei'),
            'nonce': web3.eth.get_transaction_count(sender_address),
             })

    signed_txn = web3.eth.account.sign_transaction(pancakeswap3_txn, private_key=config.private_key)
    tx_token2 = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print('Transaccion completada!!')
    print('Hash de transaccion: ', web3.toHex(tx_token2))



# define la funcion, maneja eventos e imprime en consola
def handle_event(event):
    #print(Web3.toJSON(event))
    # and whatever
    pair = Web3.toJSON(event)

    #print(pair)
    
    token0 = str(Web3.toJSON(event['args']['token1']))
    token1 = str(Web3.toJSON(event['args']['token0']))
    #block =  Web3.toJSON(event['blockNumber'])
    #txhash = Web3.toJSON(event['transactionHash'])
    #print("Block: " + block)
    #print("Txhash: " + txhash)
    print("Token0: " + token0)
    print("Token1: " + token1)
        
    wbnb2 = spend.upper()
    
    tokenToBuy2 = tokenToBuy.upper()
    
    
    if(token0.upper().strip('"') == wbnb2 and token1.upper().strip('"') == tokenToBuy2):
        print("par detectado")
        print("COMPRANDO...")
        buy()
        info_check()
        input("presione enter para vender todos los tokens")
        sell()
    elif(token0.upper().strip('"') == tokenToBuy2 and token1.upper().strip('"') == wbnb2):
        print("par detectado...")
        print("COMPRANDO...")
        buy()
        info_check()
        input("presione enter para vender todos los tokens")
        sell()
    else:
        print("se ha detectado un par nuevo, pero no el deseado")
        print("siguiente par...")


# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for PairCreated in event_filter.get_new_entries():
            handle_event(PairCreated)
        await asyncio.sleep(poll_interval)


# when main is called
# create a filter for the latest block and look for the "PairCreated" event for the uniswap factory contract
# run an async loop
# try to run the log_loop function above every 2 seconds
def main():
    event_filter = contract.events.PairCreated.createFilter(fromBlock='latest')
    #block_filter = web3.eth.filter('latest')
    # tx_filter = web3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter,2 )))
                # log_loop(block_filter, 2),
                # log_loop(tx_filter, 2)))
    finally:
        # close loop to free up system resources
        loop.close()

main()

