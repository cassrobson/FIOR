def FIOR(G, state, action, orderID, orderLog, originalorderAmount, starting_pool, S, totalcost):
    orderAmount = originalorderAmount
    def dfs(current_pool, visited, available_pools, totalcost, orderAmount):
        visited.add(current_pool)
        
        if sum(state["Availability"].values()) == 0:
            exhausted_result = exhaustedState(current_pool, G, S, state, action, orderAmount, totalcost)
            print(exhausted_result)
            
            if orderAmount == 0:
                return exhausted_result
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
                print("Number of bonds purchased at ", min_pool, " is: ", originalorderAmount - orderAmount)
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
            
            
            # Recursively call dfs on the next available pool
            for pool in available_neighbors:
                if pool not in visited:
                    if orderAmount == 0:
                        return totalcost
                    dfs(pool, visited, available_pools, totalcost, orderAmount)
        
        return totalcost
    visited = set()
    starting_pools = list(G.keys())
    starting_pools.sort(key=lambda pool: action["AskPrice"][pool])  # Sort starting pools by ask prices
    finalcost = dfs(starting_pools[0], visited, starting_pools, totalcost, orderAmount)


    return [starting_pools], finalcost

def exhaustedState(starting_pool, G, S, state, action, orderAmount, totalcost):
    print(orderAmount)
    slippage_exchanges = []
    visited = set()
    
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
            orderAmount -= 10

        elif orderAmount <= 10:
            slippage_exchanges.append((current_pool, min_pool))
            orderticket = orderAmount * (1 + min_slippage / 100) * action["AskPrice"][min_pool]
            orderAmount = 0

        totalcost += orderticket
        
        

    return slippage_exchanges, totalcost

'''

            
def transition(action, state, pool):
            # Update Availability
            state["Availability"][pool] -= state["OrderVolume"]

            # Update Exhaustion
            state["Exhaustion"][pool] = 1 if action["AskPrice"][pool] <= state["Availability"][pool] else 0

        # Reward calculation
def reward(state, action):
            total_cost = sum(action["AskPrice"][pool] * state["Availability"][pool] for pool in state["Availability"])
            return total_cost
'''