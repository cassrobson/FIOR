from scipy.optimize import minimize
import numpy as np
from newmain import *

def FIOR_LP(G, state, action, orderID, orderLog, originalorderAmount, starting_pool, S, totalcost):
    print("We are about to commance the smart order routing process for: ", originalorderAmount, " ", orderID)
    print("We will begin at pool -->", starting_pool)
    orderAmount = originalorderAmount
    visited = set()
    order_exhausted = [False]
    previous_node = starting_pool
    next_node = optimal_node_LP(G, state, starting_pool, previous_node)
    
    while sum(state["Availability"].values()) > 0:
        # Execute action
        totalcost, pool_traversed, orderticket, orderAmount = transition(next_node, visited, G, state, action, orderAmount, order_exhausted, S, totalcost, originalorderAmount)
        previous_node = starting_pool
        starting_pool = pool_traversed
        
        next_node = optimal_node_LP(G, state, starting_pool, previous_node)
        
    print("Finished at node:", pool_traversed, "We have reached the exhaustion state")
    print("Amount spent at pool ", pool_traversed, " is: ", orderticket)
    print("Number of bonds purchased at ", pool_traversed, " is: ", originalorderAmount - orderAmount)
    print("Number of bonds remaining in order is: ", orderAmount)
    print("Current total cost of the order --> ", totalcost)
    print()
    exhausted = exhaustedState(pool_traversed, G, S, state, action, orderAmount, totalcost)
    return "Pools visited -->",[visited], " --> ", exhausted

def optimal_node_LP(G, state, starting_node, previous_node):
    # Extract nodes and ask prices
    print("Previous Node: ", previous_node)
    print("Currently at node: ", starting_node)
    neighbors = G.get(starting_node, [])
    print("All direct neighbors --> ", neighbors)
    neighbors_with_availability = [node for node in neighbors if state["Availability"][node] > 0]
    print("All direct neighbors with bonds available --> ", neighbors_with_availability)
    ask_prices = [state["AskPrice"][node] for node in neighbors_with_availability]
    print("Ask prices of direct neighbors with bonds available --> ", ask_prices)
    # Number of nodes
    num_neighbors = len(neighbors_with_availability)
    # if all other askprices are zero, we can buy from any neighboring pools, if all other ask_prices are more than the starting nodes ask price, return starting node
    if all(state["AskPrice"][node] == 0 or (state["AskPrice"][starting_node] < state["AskPrice"][node] and state["Availability"][starting_node] != 0) for node in neighbors_with_availability):
        print("im here")
        return previous_node
    elif (len(neighbors_with_availability) == 0):
        #return to the node before starting node
        print("im here toooo")
        return starting_node
    else:
        # Initialize the solution vector
        x0 = np.zeros(num_neighbors)

        # Initialize the objective function coefficients
        c = [-price for price in ask_prices]

        # Bounds for the variables (ask prices must be greater than 0)
        bounds = [(0, None) for _ in range(num_neighbors)]

        # Objective function to minimize
        def objective_function(x):
            return np.dot(c, x)

        # Constraint: each node can be visited at most once
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}

        # Solve the linear programming problem
        result = minimize(objective_function, x0, bounds=bounds, constraints=constraints)

        # Extract the index of the optimal node
        optimal_node_index = np.argmax(result.x)
    previous_node = starting_node
    # Return the optimal node
    return neighbors_with_availability[optimal_node_index]

def transition(pool_to_traverse, visited, G, state, action, orderAmount, order_exhausted, S, totalcost, originalorderAmount):
    visited.add(pool_to_traverse)
    
    if sum(state["Availability"].values()) == 0:
        exhausted_result = exhaustedState(pool_to_traverse, G, S, state, action, orderAmount, totalcost)
        print(exhausted_result)
        order_exhausted[0] = True
    else:
        if orderAmount < state["Availability"][pool_to_traverse]:
            orderticket = orderAmount * state["AskPrice"][pool_to_traverse]
            state["Availability"][pool_to_traverse] -= orderAmount
            orderAmount = 0
        else:
            orderticket = state["Availability"][pool_to_traverse] * state["AskPrice"][pool_to_traverse]
            orderAmount -= state["Availability"][pool_to_traverse]
            state["Availability"][pool_to_traverse] = 0
        totalcost += orderticket
    pool_traversed = pool_to_traverse
    
    return totalcost, pool_traversed, orderticket, orderAmount

def exhaustedState(starting_pool, G, S, state, action, orderAmount, totalcost):
    print("-----------------Exhaustion State--------------------")
    print("--------This means that there remain no pools with bonds available at their original price----------")
    print("------Here is when slippage takes affect on the price of market orders--------")
    print()
    print("Remaining number of bonds to buy as market orders --> ", orderAmount)
    print("We are currently at pool --> ", starting_pool)
    slippage_exchanges = []
    visited = set()
    slippage_cost = 0
    
    while orderAmount > 0:
        current_pool = starting_pool
        visited.add(current_pool)
        available_neighbors = [pool for pool in G[current_pool] if pool in state["AskPrice"] and state["AskPrice"][pool] != 0]
        available_neighbors.sort(key=lambda pool: state["AskPrice"][pool])

        min_pool = None
        min_slippage = float('inf')

        for pool in available_neighbors:
            if pool not in visited and state["Slippages"].get((current_pool, pool)) is not None and S[(current_pool, pool)] < min_slippage:
                print("We've identified the accessable and minimal slippage as --> ", state["Slippages"].get((current_pool, pool)), " between ", current_pool, " and ", pool)
                min_pool = pool
                min_slippage = S[(current_pool, pool)]

        if orderAmount > 10:
            slippage_exchanges.append((current_pool, min_pool))
            orderticket = 10 * (1 + min_slippage / 100) * state["AskPrice"][min_pool]
            slippage_cost += (10 * (1 + min_slippage / 100) * state["AskPrice"][min_pool]) - (10 * state["AskPrice"][min_pool])
            orderAmount -= 10

        elif orderAmount <= 10:
            slippage_exchanges.append((current_pool, min_pool))
            orderticket = orderAmount * (1 + min_slippage / 100) * state["AskPrice"][min_pool]
            slippage_cost += (orderAmount * (1 + min_slippage / 100) * state["AskPrice"][min_pool]) - (orderAmount * state["AskPrice"][min_pool])
            orderAmount = 0

        totalcost += orderticket
        
        
        
        

    return "Slippage Exchange Route: " , slippage_exchanges, "Total Cost of entire order: ", totalcost, "Slippage Cost: ", slippage_cost
