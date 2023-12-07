from scipy.optimize import linprog
import numpy as np
def FIOR_LP(G, state, action, orderID, orderLog, originalorderAmount, starting_pool, S, totalcost):
    orderAmount = originalorderAmount
    visited = set()

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
        totalcost = execute_action(next_pool, visited, G, state, action, orderAmount, S, totalcost, originalorderAmount)
    totalcost = exhaustedState(starting_pool,  G, S, state, action, orderAmount, totalcost)
    return [visited], totalcost


def execute_action(current_pool, visited, G, state, action, orderAmount, order_exhausted, S, totalcost, originalorderAmount):
    visited.add(current_pool)

    if sum(state["Availability"].values()) == 0:
        exhausted_result = exhaustedState(current_pool, G, S, state, action, orderAmount, totalcost)
        print(exhausted_result)
        order_exhausted[0] = True
    else:
        neighbors = G.get(current_pool, [])

        available_neighbors = [pool for pool in neighbors if pool in state["Availability"] and state["Availability"][pool] != 0]
        available_neighbors.sort(key=lambda pool: state["AskPrice"][pool])

        min_pool = available_neighbors[0]

        orderticket = state["Availability"][min_pool] * state["AskPrice"][min_pool]
        if orderAmount < state["Availability"][min_pool]:
            orderticket = orderAmount * state["AskPrice"][min_pool]
            state["Availability"][min_pool] -= orderAmount
            orderAmount = 0
        else:
            orderAmount -= state["Availability"][min_pool]
            state["Availability"][min_pool] = 0
        totalcost += orderticket

        print("Pool with the next most optimal ask price is:", min_pool)
        print("Amount spent at pool ", min_pool, " is: ", orderticket)
        print("Number of bonds purchased at ", min_pool, " is: ", originalorderAmount - orderAmount)
        print("Number of bonds remaining in order is: ", orderAmount)
        print("Current total cost of the order --> ", totalcost)
        print()

    return totalcost

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
        
        

    return "Slippage Exchange Route: " , slippage_exchanges, "Total Cost: ", totalcost, "Slippage Cost: ", slippage_cost


