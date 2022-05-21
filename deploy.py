from solcx import compile_standard, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv
import os


load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to ganache
w3 = Web3(Web3.HTTPProvider(os.getenv("URL")))
chain_id = int(os.getenv("CHAIN_ID"))
my_address = os.getenv("ADDRESS")

# Run this command to add to global system variables export PRIVATE_KEY=eddc8b7808273f57bf77debdb2f27ad9afc3e8ae1ac7a650cd624afd386b93d6
# private_key = os.getenv("PRIVATE_KEY")

# Alternate way of doing it with regular .env file
private_key = os.getenv("PRIVATE_KEY")
# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# Build transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

# Send this signed transaction
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Working with the contract
# Contract Address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call => Simulate making the call and getting return value
# Transact => attempt to make a state change

# Initilal value of facvorite number
print(simple_storage.functions.retrieve().call())
# print(simple_storage.functions.store(15).call())


store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)

signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)

send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

print("Updated!")
print(simple_storage.functions.retrieve().call())
