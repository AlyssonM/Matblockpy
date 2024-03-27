import numpy as np
import json
from web3 import Web3

with open("./abis/PowerGen.json") as f:
        info_json = json.load(f)
abi = info_json["abi"]
contract_addr = info_json["networks"]["1515"]["address"]
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs={'timeout': 240}))
gen = w3.eth.contract(address=contract_addr, abi=abi)
user = w3.eth.accounts[0]

def setGeneratorPower(Active, Reactive):
    gen.functions.setGenPwr(Active, Reactive).transact({"from": user})
    
def getGenerator():
    data =  gen.functions.getGen().call()
    return np.array(data)
    
def PowerChangeListen():
    logs = gen.events.PowerChange().get_logs(fromBlock=w3.eth.block_number)
    for log in logs:
        print('Active Power = {} \nReactive Power = {}'.format(log.args['ActivePower'], log.args['ReactivePower']))
        
    