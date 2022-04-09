from web3 import Web3
import time
import config

print(" ")

#conectando a la bsc
bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))

if web3.isConnected():
    print(f'Conectado a BSC Mainnet')
else:
    print(f'Falla en conectar a BSC Mainnet, intente de nuevo.')
    quit()


#pancakeswap router
panRouterContractAddress = '0x10ED43C718714eb63d5aA57B78B54704E256024E'

#pancakeswap router abi 
panabi = (config.panabi)

#abi to sell
sellAbi = (config.sellAbi)

sender_address =  config.wallet_bsc
#print(sender_address)

balance = web3.eth.get_balance(sender_address)
#print(balance)
 
humanReadable = web3.fromWei(balance,'ether')
print('Balance Smart Chain: ', humanReadable)


#cantidad a comprar

tokenValue= web3.toWei(config.inversion, 'ether')

#DIRECCION DE CONTRATO DEL TOKEN A COMPRAR
tokenToBuy = web3.toChecksumAddress(input("Contrato de moneda a comprar: "))
 

#moneda con la que se va a pagar
spend = web3.toChecksumAddress(config.busd)  #CONTRATO MONEDA A PAGAR

#SETUP contrato PancakeSwap
contract = web3.eth.contract(address=panRouterContractAddress, abi=panabi)
 
#bucle while es solo para probar si compra apenas agreguen liquidez
conteo=0
while conteo<1:
    try:
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
        conteo+=1
    except:
        continue

#checar si e token esta aprobado para su venta

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


input("presione enter para vender todos los tokens")
#venta del token

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
        
