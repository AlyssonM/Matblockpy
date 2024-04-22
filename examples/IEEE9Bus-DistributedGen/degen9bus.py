import requests
import json
from cryptography.fernet import Fernet
import numpy as np
from web3 import Web3
from Crypto.Hash import SHA256
from scipy.io import savemat
from scipy.io import loadmat
from scipy.optimize import linprog
#from scipy.optimize import differential_evolution

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
        TOUp.append(Web3.to_wei(TOU[i],"ether"))
        #TOUp.append(int(TOU[i]))
    
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
    #print(PWRp)
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
    #print(response.text)
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
    else:
        print('Erro ao baixar o arquivo.')
    
    # Caminho do arquivo criptografado
    encrypted_file_path = client + '.enc'

    # Caminho onde o arquivo descriptografado será salvo
    decrypted_file_path = client + '_uncrypted.mat'

    # Descriptografar o arquivo
    decrypt_file(encrypted_file_path, decrypted_file_path, key)
    data = loadmat(decrypted_file_path)
    #print(data['Price'])
    #print(data['Quantity'])
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
    MCP = []
    MCQ = []
    #MCP_opt = []
    #MCQ_opt = []
    #LEM_opt= []
    # Exibir resultados para verificação
    #for hour in range(24):
        #print(f"Hour {hour}:")
        #print("  Buyers:", buy_bids[hour])
        #print("  Sellers:", sell_bids[hour])
        # Nb = len(buy_bids[hour])
        # Ns = len(sell_bids[hour])
        # buy_prices = []
        # buy_quantities = []
        # sell_prices = []
        # sell_quantities = []
        
        # for price, quantity, _ in buy_bids[hour]:
        #     buy_prices.append(price)
        #     buy_quantities.append(abs(quantity))
        # # Extrair os dados dos lances de venda
        # for price, quantity, _ in sell_bids[hour]:
        #     sell_prices.append(price)
        #     sell_quantities.append(quantity)

        #TOU = Web3.from_wei(DLEM.functions.getRetailPrice(hour).call(), "ether")
        # Combinação dos preços para formar Ct
        # Ct = sell_prices + [-price for price in buy_prices]
        # MCQi, MCPi = double_auction(Ns, Nb, sell_quantities, buy_quantities, Ct)
        # MCP_opt.append(MCPi)
        # MCQ_opt.append(MCQi)
        #result = maximize_social_welfare(Ns, Nb, MCQi[0:Ns], MCQi[Ns:], MCPi[0:Ns],  MCPi[Ns:], TOU)
        # result = maximize_social_welfare(Ns, Nb, MCQi, MCPi, TOU)
        # LEM_opt.append(result['y'])

    # MCQ_opt = np.array(MCQ_opt) 
    # MCP_opt = np.array(LEM_opt) 
    #LEM_opt = np.array(LEM_opt) 
    # Encontrar o preço de fechamento do mercado
    MCP, MCQ = find_market_clearing_price_hourly(buy_bids, sell_bids)

    print('MCP/MCQ ')
    print(MCP)
    print(MCQ)
    
def find_market_clearing_price_hourly(buy_bids_hourly, sell_bids_hourly):
    market_clearing_prices = np.zeros(24)
    market_clearing_quantities = np.zeros(24)
    trades = []
    for hour in range(24):
        buy_bids = buy_bids_hourly[hour]  # Assumindo que está ordenado: preço decrescente
        sell_bids = sell_bids_hourly[hour]  # Assumindo que está ordenado: preço crescente
        
        i, j = 0, 0
        accumulated_demand, accumulated_supply = 0, 0
        while i < len(buy_bids) and j < len(sell_bids):
            buy_price, buy_qty, buyer_id = buy_bids[i]
            sell_price, sell_qty, seller_id = sell_bids[j]
            #print('hour {} - buyer {}: price={} quantity={}'.format(hour,i,buy_price,buy_qty))
            #print('hour {} - seller {}: price={} quantity={}'.format(hour,j,sell_price,sell_qty))
            if buy_price >= sell_price:
                traded_qty = min(abs(buy_qty), sell_qty)
                accumulated_demand += traded_qty
                accumulated_supply += traded_qty
                if(traded_qty > 0):
                    trade = {'buyer': buyer_id, 'seller': seller_id, 'quantity': traded_qty, 'hour': hour, 'price': 0}
                    trades.append(trade)
                    

                # Atualizando quantidades nos lances
                buy_bids[i] = (buy_price, -(abs(buy_qty) - traded_qty), buy_bids[i][2])
                sell_bids[j] = (sell_price, sell_qty - traded_qty, sell_bids[j][2])

                # Avançar nos lances quando a quantidade se esgota
                if abs(buy_bids[i][1]) <= 0:
                    i += 1
                if sell_bids[j][1] <= 0:
                    j += 1

                # Definindo MCP e MCQ para a hora atual
                market_clearing_price = sell_price  # MCP pode ser definido como preço de venda ou de compra
                market_clearing_quantity = accumulated_demand
            else:
                break

        market_clearing_prices[hour] = market_clearing_price if market_clearing_quantity > 0 else 0
        market_clearing_quantities[hour] = market_clearing_quantity if market_clearing_quantity > 0 else 0

    
    for trade in trades:
        trade['price'] = market_clearing_prices[trade['hour']]
        #print(trade)
        register_trade(trade)
        
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
                trade = {'buyer': buyer_id, 'seller': seller_id, 'quantity': trade_quantity, 'hour': hour, 'price': mcp}
                trades.append(trade)
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

def register_trade(trade):
    DLEM.functions.addTransaction(
        trade['buyer'],
        trade['seller'],
        trade['hour'],
        Web3.to_wei(trade['quantity'],"ether"),
        Web3.to_wei(trade['price'],"ether")
        ).transact({"from": DSO})
    
def getTransactions():
    return DLEM.functions.getTransactions().call()

def double_auction(Ns, Nb, Ps, Pb, Ct):
    N = Ns + Nb
    P = np.concatenate([Ps, Pb])  # Combina os preços de vendedores e compradores

    # Definindo os coeficientes para a função objetivo
    C = np.array(Ct)  # Usamos negativo porque linprog faz minimização

    # As restrições de desigualdade (x >= 0 e x <= P)
    # linprog usa a forma Ax <= b para restrições, então para x >= 0, não precisamos definir (já é implícito)
    A_ub = np.vstack([np.eye(N), -np.eye(N)])  # x <= Ps/Pb e x >= 0
    b_ub = np.concatenate([Ps, Pb, np.zeros(N)])  # Limites superiores e x >= 0
    
    
    # Restrição de igualdade para garantir que a oferta e demanda sejam iguais
    A_eq = np.ones((1, N))
    A_eq[0, :Ns] = -1  # Coeficientes para vendedores
    A_eq[0, Ns:] = 1  # Coeficientes para compradores
    b_eq = [0]

    # Resolver o problema de otimização linear
    result = linprog(C, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, method='highs')

    MCQ = result.x  # Quantidades ótimas
    lambda_ = C  # Valor ótimo da função objetivo (negativo devido à inversão inicial)

    return MCQ, lambda_

def maximize_social_welfare(Ns, Nb, P, C, TOU):
    # Definindo os coeficientes da função objetivo (maximizar -Ct * y)
    #Ct = np.concatenate(([0], -np.array(P[:Ns]), -np.array(P[Ns:])))
    Ct = np.concatenate(([1], -np.array(P)))
    # Criando a matriz A e o vetor b das restrições de desigualdade
    A = np.zeros((Ns + Nb + 6, Ns + Nb + 1))
    b = np.zeros(Ns + Nb + 6)

    # Preenchendo as restrições para vendedores
    for j in range(Ns):
        A[j, 0] = 1  # Coeficiente para lambda_m
        A[j, j + 1] = -1  # Coeficiente para nu_Sj
        #b[j] = -Cs[j]  # Limite superior P_Sj
        b[j] = C[j]

    # Preenchendo as restrições para compradores
    for i in range(Nb):
        A[Ns + i, 0] = -1  # Coeficiente negativo para lambda_m
        A[Ns + i, Ns + i + 1] = -1  # Coeficiente para nu_Bi
        #b[Ns + i] = -Cb[i]  # Limite superior negativo -P_Bi
        b[Ns + i] = C[Ns+i]
    
    for j in range(Ns+Nb):
        A[Ns+Nb+j, j + 1] = -1
        b[Ns+Nb+j] = 0
    
    #print(A)
    #print(b)    
    #bounds = [(0, TOU) for _ in range(Ns + Nb + 1)]
    bounds = [(None, None)] + [(0, TOU)] * (Ns + Nb) 
    # Chamando o solucionador de otimização linear
    res = linprog(Ct, A_ub=A, b_ub=b, bounds=bounds, method='highs')

    # Verificando o sucesso da otimização e retornando o resultado
    if res.success:
        return {'y': res.x, 'social_welfare': -res.fun}
    else:
        raise ValueError("A otimização falhou: " + res.message)


