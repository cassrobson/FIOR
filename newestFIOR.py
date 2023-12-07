from scipy.optimize import linprog
import numpy as np
from main import *
def FIOR_LP(G, state, action, orderID, orderLog, originalorderAmount, starting_pool, S, totalcost):
    orderAmount = originalorderAmount
    visited = set()
    order_exhausted = [False]
    starting_pools = list(G.keys())
    starting_pools.sort(key=lambda pool: state["AskPrice"][pool]) 
    # Linear Programming: Define the objective function coefficients (costs)
    c = [state["AskPrice"][pool] for pool in action["AvailablePools"]]

    while sum(state["Availability"].values()) > 0:
        # Linear Programming: Define the inequality constraints (availability constraints)
        A = [[-1 if pool == target else 0 for target in action["AvailablePools"]] for pool in action["AvailablePools"]]
        b = [0] * len(action["AvailablePools"])

        # Linear Programming: Solve the linear program
        result = linprog(c, A_ub=A, b_ub=b)

        # Get the next pool to execute the order
        next_pool_index = np.argmin(result.x)
        next_pool = action["AvailablePools"][next_pool_index]

        # Execute action
        totalcost, min_pool, orderticket, orderAmount = transition(next_pool, visited, starting_pools, G, state, action, orderAmount, order_exhausted, S, totalcost, originalorderAmount)
        print("Pool with the next most optimal ask price is:", min_pool)
        print("Amount spent at pool ", min_pool, " is: ", orderticket)
        print("Number of bonds purchased at ", min_pool, " is: ", originalorderAmount - orderAmount)
        print("Number of bonds remaining in order is: ", orderAmount)
        print("Current total cost of the order --> ", totalcost)
        print()
        
        
    return [visited], totalcost


def transition(current_pool, visited, available_pools, G, state, action, orderAmount, order_exhausted, S, totalcost, originalorderAmount):
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
        available_neighbors.sort(key=lambda pool: state["AskPrice"][pool])

        min_pool = None
        min_ask_price = float('inf')  # Initialize with positive infinity
        for pool in available_neighbors:
            if pool not in visited and state["AskPrice"][pool] < min_ask_price:
                min_pool = pool
                min_ask_price = state["AskPrice"][pool]

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

        # Check if orderAmount is still greater than 0 before attempting to execute at any available pool
        for pool in available_pools:
            if pool not in visited:
                orderticket_pool = state["Availability"][pool] * state["AskPrice"][pool]
                if orderAmount < state["Availability"][pool]:
                    orderticket_pool = orderAmount * state["AskPrice"][pool]
                    state["Availability"][pool] -= orderAmount
                    orderAmount = 0
                else:
                    orderAmount -= state["Availability"][pool]
                    state["Availability"][pool] = 0
                totalcost += orderticket_pool
        
        # Recursively call transition on the next available pool
        for pool in available_neighbors:
            if pool not in visited and not order_exhausted[0]:
                transition(pool, visited, available_pools, totalcost, orderAmount,order_exhausted, state, action, G, originalorderAmount, S)
    
    return totalcost, min_pool, orderticket, orderAmount

def exhaustedState(starting_pool, G, S, state, action, orderAmount, totalcost):
    print(orderAmount)
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
            if pool not in visited and S.get((current_pool, pool)) is not None and S[(current_pool, pool)] < min_slippage:
                min_pool = pool
                min_slippage = S[(current_pool, pool)]

        if min_pool is not None:  # Check if a valid pool is found
            if orderAmount > 10:
                slippage_exchanges.append((current_pool, min_pool))
                # Linear Programming: Define the objective function coefficients (slippage costs)
                c = [S[(current_pool, min_pool)] for _ in available_neighbors]

                # Linear Programming: Define the equality constraints (allocate 10 bonds)
                A_eq = [[1 if pool == min_pool else 0 for pool in available_neighbors]]
                b_eq = [10]

                # Linear Programming: Solve the linear program
                result = linprog(c, A_eq=A_eq, b_eq=b_eq)

                orderticket = 10 * (1 + result.fun / 100) * state["AskPrice"][min_pool]
                slippage_cost += (10 * (1 + result.fun / 100) * state["AskPrice"][min_pool]) - (10 * state["AskPrice"][min_pool])
                orderAmount -= 10

            elif orderAmount <= 10:
                slippage_exchanges.append((current_pool, min_pool))
                # Linear Programming: Define the objective function coefficients (slippage costs)
                c = [S[(current_pool, min_pool)] for _ in available_neighbors]

                # Linear Programming: Define the equality constraints (allocate remaining bonds)
                A_eq = [[1 if pool == min_pool else 0 for pool in available_neighbors]]
                b_eq = [orderAmount]

                # Linear Programming: Solve the linear program
                result = linprog(c, A_eq=A_eq, b_eq=b_eq)

                orderticket = orderAmount * (1 + result.fun / 100) * state["AskPrice"][min_pool]
                slippage_cost += (orderAmount * (1 + result.fun / 100) * state["AskPrice"][min_pool]) - (orderAmount * state["AskPrice"][min_pool])
                orderAmount = 0

            totalcost += orderticket
        else:
            break  # Break out of the loop if no valid pool is found

    return "Slippage Exchange Route: ", slippage_exchanges, "Total Cost: ", totalcost, "Slippage Cost: ", slippage_cost
