from scipy.optimize import minimize
import numpy as np
from newmain import *

def FIOR_LP(G, state, action, orderID, orderLog, originalorderAmount, starting_pool, S, totalcost):
    print()
    print("-----------------ORDER INITIALIZED------------------")
    print("We are about to commance the smart order routing process (MDP) using linear programming and optimization for: ", originalorderAmount, " ", orderID)
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
    slippage_exchanges, totalcost, slippage_cost, reward = exhaustedState(pool_traversed, G, S, state, action, orderAmount, totalcost, originalorderAmount)
    print()
    print("-------SUMMARY OF ORDER EXECUTION----------")
    print()
    print("Slippage Exchange Route: " , slippage_exchanges, "Total Cost of entire order: ", totalcost, "Slippage Cost: ", slippage_cost)
    return "Pools visited -->",[visited], " --> ", reward

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
    print("-----------------------------------------------------------------")
    # Number of nodes
    num_neighbors = len(neighbors_with_availability)
    # if all other askprices are zero, we can buy from any neighboring pools, if all other ask_prices are more than the starting nodes ask price, return starting node
    if all(state["AskPrice"][node] == 0 or (state["AskPrice"][starting_node] < state["AskPrice"][node] and state["Availability"][starting_node] != 0) for node in neighbors_with_availability):
        return previous_node
    elif (len(neighbors_with_availability) == 0):
        #return to the node before starting node
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

def exhaustedState(starting_pool, G, S, state, action, orderAmount, totalcost, originalorderAmount):
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

        min_pool, min_slippage = optimal_slippage_LP(current_pool, available_neighbors, S)
        print("Minimum accessible slippage route identified --> ", min_slippage, " ", (current_pool, min_pool))
        
        if orderAmount > 10:
            slippage_exchanges.append((current_pool, min_pool))
            orderticket = 10 * (1 + min_slippage / 100) * state["AskPrice"][min_pool]
            slippage_cost += (10 * (1 + min_slippage / 100) * state["AskPrice"][min_pool]) - (10 * state["AskPrice"][min_pool])
            orderAmount -= 10
            print("Order of 10 bonds submitted at pool ", min_pool, " with slippage cost of ", slippage_cost)

        elif orderAmount <= 10:
            slippage_exchanges.append((current_pool, min_pool))
            orderticket = orderAmount * (1 + min_slippage / 100) * state["AskPrice"][min_pool]
            slippage_cost += (orderAmount * (1 + min_slippage / 100) * state["AskPrice"][min_pool]) - (orderAmount * state["AskPrice"][min_pool])
            orderAmount = 0
            print("Remaining number of bonds purchased at pool ", min_pool, " with slippage cost of ", slippage_cost)

        totalcost += orderticket
    print()
    
    print("-------REWARD CALCULATION--------")   
    reward = calculate_reward(state, orderAmount, totalcost, slippage_cost, originalorderAmount)
    return slippage_exchanges, totalcost, slippage_cost, reward

def optimal_slippage_LP(current_pool, available_neighbors, S):
    # Initialize the solution vecotr for slippage optimization
    x0 = np.zeros(len(available_neighbors))
    
    #Initialize the objective function coefficiencts
    c = [S.get((current_pool, pool), 0) for pool in available_neighbors]
    
    #Bounds for the variables (slippages must be greater than or equal to zero)
    bounds = [(0, None) for _ in range(len(available_neighbors))]
    
    #Objective function to minimize
    def objective_function(x):
        return np.dot(c, x)
    
    #Contraint: only one neighbor can be chosen
    constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
    
    #Solve the linear programming problem to find the minimum slippage
    result = minimize(objective_function, x0, bounds=bounds, constraints=constraints)
    
    #Extract the index of the optmal neighbor (minimal slippage)
    optimal_neighbor_index = np.argmax(result.x)
    
    return available_neighbors[optimal_neighbor_index], S.get((current_pool, available_neighbors[optimal_neighbor_index]), 0)
    
def calculate_reward(state, orderAmount, totalcost, slippage_cost, originalorderAmount):
    # Reward based on the number of bonds purchased
    if orderAmount == 0:
        orderFulfilledReward = 1
        print("We successfully fulfilled the customers order")
    else: 
        orderFulfilledReward = -1
        print("Order not completely fulfilled, customer has moved to another market maker because we failed to please")

    # Reward based on slippage cost
    if slippage_cost > (0.02 * totalcost):  # Penalize for slippage cost
        slippage_cost_penalty = -1
        print("Slippage cost exceeded the 2% threshold and we have failed to meet our customer guarantee")
    else: 
        slippage_cost_penalty = 1
        print("We successfully kept slippage cost to under 2 percent of the total cost of the order")
    # Reward based on total cost of the order
    ask_prices = [state["AskPrice"][price] for price in state["AskPrice"] if state["AskPrice"][price] > 0]
    averageprice = sum(ask_prices) / (len(ask_prices))
    averagethreshold = originalorderAmount * averageprice
    
    if totalcost < averagethreshold:
        costefficiencyreward = 1
        print("We have saved the customer money on average using smart order routing")
    else:
        costefficiencyreward = -1
        print("Our total cost for the order failed to fall below the cost of buying the bonds at an average ask price")
    # Combine individual rewards (you can adjust weights if needed)
    combined_reward = orderFulfilledReward + slippage_cost_penalty + costefficiencyreward

    return "OVERALL REWARD --> ", combined_reward