from main import *
import random
def FIOR(G, state, action, orderID, orderLog, originalorderAmount, starting_pool, S, totalcost):
    print("We are about to commance the smart order routing process (MDP) using DFS Traversal for: ", originalorderAmount, " ", orderID)
    print("We will begin at pool -->", starting_pool)
    orderAmount = originalorderAmount
    order_exhausted = [False]  # List to store the order exhaustion state
    visited = set()
    starting_pools = list(G.keys())
    starting_pools.sort(key=lambda pool: action["AskPrice"][pool])

    finalcost = transition(starting_pools[0], visited, starting_pools, totalcost, orderAmount, order_exhausted, state, action, G, originalorderAmount, S)

    return [starting_pools], finalcost

def transition(current_pool, visited, available_pools, totalcost, orderAmount, order_exhausted, state, action, G, originalorderAmount, S):
    visited.add(current_pool)
    
    if sum(state["Availability"].values()) == 0:
        exhausted_result = exhaustedState(current_pool, G, S, state, action, orderAmount, totalcost)
        print(exhausted_result)
        order_exhausted[0] = True
    else:
        neighbors = G.get(current_pool, [])  # Directly access neighbors from the graph

        # Find available neighbors and sort them by ask prices
        available_neighbors = [pool for pool in neighbors
                            if pool in state["Availability"] and state["Availability"][pool] != 0]
        available_neighbors.sort(key=lambda pool: action["AskPrice"][pool])

        min_pool = None
        min_ask_price = float('inf')  # Initialize with positive infinity
        for pool in available_neighbors:
            if pool not in visited and action["AskPrice"][pool] < min_ask_price:
                min_pool = pool
                min_ask_price = action["AskPrice"][pool]

        if min_pool is not None:
            orderticket = state["Availability"][min_pool] * min_ask_price
            if orderAmount < state["Availability"][min_pool]:
                orderticket = orderAmount * min_ask_price
                state["Availability"][min_pool] -= orderAmount
                orderAmount = 0
            else:
                orderAmount -= state["Availability"][min_pool]
                state["Availability"][min_pool] = 0
            totalcost += orderticket
            
            print("Pool with the next most optimal ask price is:", min_pool)
            print("Amount spent at pool ", min_pool, " is: ", orderticket)
            print("Number of bonds purchased so far ", min_pool, " is: ", originalorderAmount - orderAmount)
            print("Number of bonds remaining in order is: ", orderAmount)
            print("Current total cost of the order --> ", totalcost)
            print()

        # Check if orderAmount is still greater than 0 before attempting to execute at any available pool
        for pool in available_pools:
            if pool not in visited:
                orderticket_pool = state["Availability"][pool] * action["AskPrice"][pool]
                if orderAmount < state["Availability"][pool]:
                    orderticket_pool = orderAmount * action["AskPrice"][pool]
                    state["Availability"][pool] -= orderAmount
                    orderAmount = 0
                else:
                    orderAmount -= state["Availability"][pool]
                    state["Availability"][pool] = 0
                totalcost += orderticket_pool
                
                print("Pool with the next most optimal ask price is:", pool)
                print("Amount spent at pool ", pool, " is: ", orderticket_pool)
                print("Number of bonds purchased at ", pool, " is: ", originalorderAmount - orderAmount)
                print("Number of bonds remaining in order is: ", orderAmount)
                print("Current total cost of the order --> ", totalcost)
                print()
        
        
        # Recursively call transition on the next available pool
        for pool in available_neighbors:
            if pool not in visited and not order_exhausted[0]:
                transition(pool, visited, available_pools, totalcost, orderAmount,order_exhausted, state, action, G, originalorderAmount, S)
    
    return totalcost
    
def exhaustedState(starting_pool, G, S, state, action, orderAmount, totalcost):
    print("-----------------Exhaustion State--------------------")
    print("--------This means that there remain no pools with bonds available at their original price----------")
    print("------Here is when slippage takes affect on the price of market orders--------")
    print()
    print("Remaining number of bonds to buy as market orders --> ", orderAmount)
    print("We are currently at pool --> ", starting_pool)
    print(orderAmount)
    slippage_exchanges = []
    visited = set()
    slippage_cost = 0
    
    while orderAmount > 0:
        current_pool = starting_pool
        visited.add(current_pool)
        available_neighbors = [pool for pool in G[current_pool] if pool in action["AskPrice"] and action["AskPrice"][pool] != 0]
        available_neighbors.sort(key=lambda pool: action["AskPrice"][pool])

        min_pool = None
        min_slippage = float('inf')

        for pool in available_neighbors:
            if pool not in visited and S.get((current_pool, pool)) is not None and S[(current_pool, pool)] < min_slippage:
                min_pool = pool
                min_slippage = S[(current_pool, pool)]

        if orderAmount > 10:
            slippage_exchanges.append((current_pool, min_pool))
            orderticket = 10 * (1 + min_slippage / 100) * action["AskPrice"][min_pool]
            slippage_cost += (10 * (1 + min_slippage / 100) * action["AskPrice"][min_pool]) - (10 * action["AskPrice"][min_pool])
            orderAmount -= 10

        elif orderAmount <= 10:
            slippage_exchanges.append((current_pool, min_pool))
            orderticket = orderAmount * (1 + min_slippage / 100) * action["AskPrice"][min_pool]
            slippage_cost += (orderAmount * (1 + min_slippage / 100) * action["AskPrice"][min_pool]) - (orderAmount * action["AskPrice"][min_pool])
            orderAmount = 0

        totalcost += orderticket
        
        

    return "Slippage Exchange Route: " , slippage_exchanges, "Total Cost: ", totalcost, "Slippage Cost: ", slippage_cost


