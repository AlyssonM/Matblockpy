from scipy.optimize import differential_evolution
import numpy as np
from scipy.optimize import minimize

def runOpt():
    # Parâmetros de exemplo
    Ns = 10  # Número de vendedores
    Nb = 10  # Número de compradores
    sell_costs = np.random.uniform(0.1, 0.25, Ns)  # Custos aleatórios dos vendedores
    buy_valuations = np.random.uniform(0.25, 0.55, Nb)  # Valorações aleatórias dos compradores
    TOU = 0.60  # Preço máximo que os compradores estão dispostos a pagar
    feed_in_tariff = 0.45  # Preço mínimo que os vendedores estão dispostos a aceitar
    # Bounds para o problema
    bounds = [(feed_in_tariff, TOU) for _ in range(Ns)] + [(0, TOU) for _ in range(Nb)]

    # Usar um algoritmo evolutivo como Differential Evolution para encontrar a melhor configuração de preços
    result = differential_evolution(lambda x: evaluate(x, sell_costs, buy_valuations, Ns), bounds)

    # Verifique o sucesso da otimização e imprima os resultados
    if result.success:
        optimized_prices = result.x
        sell_prices_optimized = optimized_prices[:Ns]
        buy_prices_optimized = optimized_prices[Ns:]
        consumer_surplus = sum([max(0, valuation - price) for valuation, price in zip(buy_valuations, buy_prices_optimized)])
        producer_surplus = sum([max(0, price - cost) for cost, price in zip(sell_costs, sell_prices_optimized)])
        social_welfare_optimized = consumer_surplus + producer_surplus
        market_balance_optimized = abs(sum(buy_prices_optimized) - sum(sell_prices_optimized))
        print('Preços otimizados de venda:', sell_prices_optimized)
        print('Preços otimizados de compra:', buy_prices_optimized)
        print('Bem-estar social otimizado:', social_welfare_optimized)
        print('Equilíbrio de mercado otimizado:', -market_balance_optimized)
    else:
        print('Otimização falhou:', result.message)
    
def evaluate(individual, sell_costs, buy_valuations, Ns):
    sell_prices = individual[:Ns]
    buy_prices = individual[Ns:]

    # Suponha que temos pesos para cada objetivo
    weight_social_welfare = 0.5  # Peso para o bem-estar social
    weight_market_balance = 0.5  # Peso para o equilíbrio de mercado

    # Calcula o bem-estar social
    consumer_surplus = sum([max(0, valuation - price) for valuation, price in zip(buy_valuations, buy_prices)])
    producer_surplus = sum([max(0, price - cost) for cost, price in zip(sell_costs, sell_prices)])
    social_welfare = consumer_surplus + producer_surplus

    # Calcula o equilíbrio de mercado (aqui simplificado como a diferença entre compra e venda)
    market_balance = abs(sum(buy_prices) - sum(sell_prices))

    # Retorna um único valor escalar combinando os objetivos
    return weight_social_welfare * social_welfare - weight_market_balance * market_balance

# Configuração do problema
Ns = 3  # Número de vendedores
Nb = 5  # Número de compradores
min_sell_prices = np.array([0.49, 0.51, 0.53])  # Preços mínimos dos vendedores
max_buy_prices = np.array([0.56, 0.52, 0.49, 0.47, 0.46])  # Preços máximos dos compradores
sell_quantity_limits = (0, 26.754)  # Limites de quantidade que os vendedores podem vender
buy_quantity_limits = (0, 23.53)  # Limites de quantidade que os compradores podem comprar

# Função objetivo
def objective(vars):
    # p_m é o preço de fechamento de mercado
    p_m = vars[0]
    sell_quantities = vars[1:Ns+1]
    buy_quantities = vars[Ns+1:]

    # Calcula o bem-estar social como um escalar
    consumer_surplus = sum((max_buy_prices[i] - p_m) * buy_quantities[i] for i in range(Nb) if p_m <= max_buy_prices[i])
    producer_surplus = sum((p_m - min_sell_prices[i]) * sell_quantities[i] for i in range(Ns) if p_m >= min_sell_prices[i])
    
    social_welfare = consumer_surplus + producer_surplus

    return -social_welfare  # Negativo para maximizar na otimização

# Restrição de equilíbrio de mercado
def market_balance(vars):
    sell_quantities = vars[1:Ns+1]
    buy_quantities = vars[Ns+1:]
    return sum(sell_quantities) - sum(buy_quantities)

# Limites para as variáveis
bounds = [(0.47, 0.62)] + [sell_quantity_limits] * Ns + [buy_quantity_limits] * Nb

# Restrições
constraints = [{'type': 'eq', 'fun': market_balance}]

# Ponto de partida para a otimização
initial_guess = np.random.rand(1 + Ns + Nb)  # Inicialização aleatória

# Executar a otimização
result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

if result.success:
    optimized_vars = result.x
    market_price_optimized = optimized_vars[0]
    sell_quantities_optimized = optimized_vars[1:Ns+1]
    buy_quantities_optimized = optimized_vars[Ns+1:]

    print('Preço de fechamento de mercado otimizado:', market_price_optimized)
    print('Quantidades de venda otimizadas:', sell_quantities_optimized)
    print('Quantidades de compra otimizadas:', buy_quantities_optimized)
else:
    print('Otimização falhou:', result.message)

#runOpt()

