import requests
import json
from cryptography.fernet import Fernet
import numpy as np
from web3 import Web3
from Crypto.Hash import SHA256
from scipy.io import savemat
from scipy.io import loadmat

with open("./abis/DLEM.json") as f:
        info_json = json.load(f)
abi = info_json["abi"]
contract_addr = info_json["networks"]["1515"]["address"]
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs={'timeout': 240}))
DLEM = w3.eth.contract(address=contract_addr, abi=abi)
DSO = w3.eth.accounts[0]
accounts_addr = {
        'client1': w3.eth.accounts[1],
        'client2': w3.eth.accounts[2],
        'client3': w3.eth.accounts[3],
        'client4': w3.eth.accounts[4],
        'client5': w3.eth.accounts[5],
        'client6': w3.eth.accounts[6],
    }

# Gerar uma chave de criptografia
# Em um cenário real, você precisa salvar essa chave de forma segura para descriptografar o arquivo mais tarde
key = Fernet.generate_key()

cipher_suite = Fernet(key)

def encrypt_file(file_path):
    # Ler o conteúdo do arquivo
    with open(file_path, 'rb') as file:
        file_data = file.read()

    # Criptografar os dados do arquivo
    encrypted_data = cipher_suite.encrypt(file_data)

    # Salvar o arquivo criptografado
    encrypted_file_path = file_path + '.enc'
    with open(encrypted_file_path, 'wb') as file:
        file.write(encrypted_data)

    return encrypted_file_path

def decrypt_file(encrypted_file_path, decrypted_file_path, key):
    cipher = Fernet(key)
    # Ler o conteúdo criptografado do arquivo
    with open(encrypted_file_path, 'rb') as file:
        encrypted_data = file.read()

    # Descriptografar os dados
    decrypted_data = cipher.decrypt(encrypted_data)

    # Salvar o arquivo descriptografado
    with open(decrypted_file_path, 'wb') as file:
        file.write(decrypted_data)
        
def Register(account, user_id, role):
    hash = SHA256.new()
    hash.update(user_id.encode('utf-8'))
    hashedData = "0x" + hash.hexdigest()
    hashed_bytes = Web3.to_bytes(hexstr=hashedData)
    DLEM.functions.Register(user_id, hashed_bytes, int(role)).transact({"from": accounts_addr.get(account)})

def startLEM(TOU):
    #TOUp = (np.array((TOU.astype(int)))).tolist()
    TOUp = []
    for i in range(24):
        #TOUp.append(Web3.to_wei(TOU[i],"ether"))
        TOUp.append(int(TOU[i]))
    
    DLEM.functions.setRetailPrice(TOUp).transact({"from": DSO})
    DLEM.functions.startLEM().transact({"from": DSO})
    
    if DLEM.functions.balanceOf(accounts_addr.get('client1')).call() == 0:
        DLEM.functions.transfer(accounts_addr.get('client1'), 150000*10**18).transact({"from": DSO})
    
    if DLEM.functions.balanceOf(accounts_addr.get('client2')).call() == 0:
        DLEM.functions.transfer(accounts_addr.get('client2'), 150000*10**18).transact({"from": DSO})

    if DLEM.functions.balanceOf(accounts_addr.get('client3')).call() == 0:
        DLEM.functions.transfer(accounts_addr.get('client3'), 150000*10**18).transact({"from": DSO})
    
    if DLEM.functions.balanceOf(accounts_addr.get('client4')).call() == 0:
        DLEM.functions.transfer(accounts_addr.get('client4'), 150000*10**18).transact({"from": DSO})
    
    if DLEM.functions.balanceOf(accounts_addr.get('client5')).call() == 0:
        DLEM.functions.transfer(accounts_addr.get('client5'), 150000*10**18).transact({"from": DSO})
    
    if DLEM.functions.balanceOf(accounts_addr.get('client6')).call() == 0:
        DLEM.functions.transfer(accounts_addr.get('client6'), 150000*10**18).transact({"from": DSO})
 
def DLEMbid(Addr, Pwr, Price):
    PWRp = [0]*24
    Price_p = [0]*24
    for i in range(24):
        if(Pwr[i] < 0):
            PWRp[i] = -1*Web3.to_wei(abs(Pwr[i]), "ether")
        else:
            PWRp[i] = Web3.to_wei(Pwr[i], "ether")
        Price_p[i] = Web3.to_wei(Price[i], "ether")
    mat_dict = {'Price': Price, 'Quantity': Pwr}
    file_name = './.biddata/' + Addr + '.mat'
    savemat(file_name, mat_dict)
    ipfscid = bidIPFS(Addr)  
    print(PWRp)
    DLEM.functions.submitBid(PWRp, Price_p, ipfscid).transact({"from": accounts_addr.get(Addr)})

def bidIPFS(client):              
    # Endereço do nó IPFS
    url = 'http://127.0.0.1:5001/api/v0/add'
    # Caminho para o arquivo que você quer adicionar ao IPFS
    file_path = './.biddata/' + client + '.mat'
    # Usar a função para criptografar seu arquivo
    encrypted_file_path = encrypt_file(file_path)
    # Fazendo a requisição para a API do IPFS
    with open(encrypted_file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    # Verificando a resposta
    print(response.text)
    return response.text

def getBids():
    return DLEM.functions.getBids().call()

def getBidsLength():
    return DLEM.functions.getBidsLength().call()

def  getIPFSdata(client, ipfscid, key):
    url = f'http://127.0.0.1:5001/api/v0/cat?arg={ipfscid}'
    # Fazendo a requisição para baixar o arquivo
    response = requests.post(url)

    # Verificando se a requisição foi bem-sucedida
    if response.status_code == 200:
    # Salvando o arquivo baixado, substitua 'nome_do_arquivo' pelo nome que deseja salvar
        with open(client + '.enc', 'wb') as f:
            f.write(response.content)
        print('Arquivo baixado com sucesso.')
    else:
        print('Erro ao baixar o arquivo.')
    
    # Caminho do arquivo criptografado
    encrypted_file_path = client + '.enc'

    # Caminho onde o arquivo descriptografado será salvo
    decrypted_file_path = client + '_uncrypted.mat'

    # Descriptografar o arquivo
    decrypt_file(encrypted_file_path, decrypted_file_path, key)
    data = loadmat(decrypted_file_path)
    print(data['Price'])
    print(data['Quantity'])
    return data['Price'], data['Quantity']

def MarketData():
    clients = getBidsLength()
    bids = getBids()
    Prices = np.zeros((clients, 24))
    Quantities = np.zeros((clients, 24))
    Identifiers = ['' for _ in range(clients)]
    for c in range(clients):  
        metadata_str = bids[c][2]
        metadata = json.loads(metadata_str)
        hash_value = metadata['Hash']
        Price, Quantity = getIPFSdata('./.biddata/client' + str(c+1) , hash_value, key)
        Prices[c,:] = Price
        Quantities[c,:] = Quantity
        Identifiers[c] = bids[c][1]
    # Inicializando arrays para armazenar os lances organizados
    buy_bids = [[] for _ in range(24)]  # Compradores
    sell_bids = [[] for _ in range(24)]  # Vendedores

    # Processar cada hora do dia
    for hour in range(24):
        # Separar lances de compradores e vendedores
        for client in range(clients):
            price = Prices[client, hour]
            quantity = Quantities[client, hour]
            identifier = Identifiers[client]
            if quantity < 0:  # Comprador
                buy_bids[hour].append((price, quantity, identifier))
            else:  # Vendedor
                sell_bids[hour].append((price, quantity, identifier))
        
        # Ordenar lances por preço
        buy_bids[hour].sort(key=lambda x: x[0], reverse=True)  # Preços mais altos primeiro para compradores
        sell_bids[hour].sort(key=lambda x: x[0])  # Preços mais baixos primeiro para vendedores

    # Exibir resultados para verificação
    for hour in range(24):
        print(f"Hour {hour}:")
        print("  Buyers:", buy_bids[hour])
        print("  Sellers:", sell_bids[hour])
        
    # Encontrar o preço de fechamento do mercado
    MCP , MCQ = find_market_clearing_price_hourly(buy_bids, sell_bids)
    match_trades_hourly(buy_bids, sell_bids, MCP)
    print(MCP)
    print(MCQ)    
    
def find_market_clearing_price_hourly(buy_bids_hourly, sell_bids_hourly):
    market_clearing_prices = np.zeros(24)
    market_clearing_quantities = np.zeros(24)

    for hour in range(24):
        buy_bids = buy_bids_hourly[hour]
        sell_bids = sell_bids_hourly[hour]

        # Certifique-se de que os lances estão ordenados
        #buy_bids.sort(key=lambda x: x[0], reverse=True)  # Preços mais altos primeiro para compradores
        #sell_bids.sort(key=lambda x: x[0])  # Preços mais baixos primeiro para vendedores

        accumulated_demand = 0
        accumulated_supply = 0
        market_clearing_price = None
        market_clearing_quantity = None

        for sell in sell_bids:
            accumulated_supply += sell[1]
            accumulated_demand = 0  # Reiniciar a demanda para cada nova oferta
            for buy in buy_bids:
                #accumulated_demand += abs(buy[1])
                if(abs(buy[1]) >= sell[1]):
                    accumulated_demand += abs(sell[1])
                else:
                    accumulated_demand += abs(buy[1])

                if accumulated_demand >= accumulated_supply and accumulated_supply > 0:
                    market_clearing_price = sell[0]  # ou buy[0], dependendo da sua definição de MCP
                    market_clearing_quantity = accumulated_demand
                    break
                else:
                    market_clearing_price = 1
                    #market_clearing_quantity = accumulated_supply

            if market_clearing_price is not None:
                break

        market_clearing_prices[hour] = market_clearing_price if market_clearing_price is not None else 0
        market_clearing_quantities[hour] = market_clearing_quantity if market_clearing_quantity is not None else 0
    return market_clearing_prices, market_clearing_quantities

def match_trades_hourly(buy_bids_hourly, sell_bids_hourly, market_clearing_prices):
    hourly_trades = {}

    for hour in range(24):
        mcp = market_clearing_prices[hour]
        buy_bids = buy_bids_hourly[hour]
        sell_bids = sell_bids_hourly[hour]

        #buy_bids.sort(key=lambda x: x[0], reverse=True)
        #sell_bids.sort(key=lambda x: x[0])

        trades = []
        for sell_price, sell_quantity, seller_id in sell_bids:
            if sell_price > mcp or sell_quantity <= 0:
                continue

            for buy in list(buy_bids):
                buy_price, buy_quantity, buyer_id = buy

                if buy_price < mcp or abs(buy_quantity) <= 0:
                    continue

                trade_quantity = min(abs(buy_quantity), sell_quantity)
                trade = {'buyer': buyer_id, 'seller': seller_id, 'quantity': trade_quantity, 'price': mcp}
                trades.append({'buyer': buyer_id, 'seller': seller_id, 'quantity': trade_quantity, 'price': mcp})
                register_trade(trade,hour,buyer_id,seller_id)
                buy_quantity -= trade_quantity
                sell_quantity -= trade_quantity

                # Atualiza a quantidade restante para o comprador
                buy_bids[buy_bids.index(buy)] = (buy_price, -buy_quantity, buyer_id)

                if sell_quantity <= 0:
                    break

        hourly_trades[hour] = trades
    print(hourly_trades)
    return hourly_trades

def register_trade(trade, hour, buyer_address, seller_address):
    DLEM.functions.addTransaction(
        buyer_address,
        seller_address,
        hour,
        Web3.to_wei(trade['quantity'],"ether"),
        Web3.to_wei(trade['price'],"ether")
        ).transact({"from": DSO})
    
def getTransactions():
    return DLEM.functions.getTransactions().call()