def FIOR(G, state, action, orderID, orderLog, orderAmount, starting_pool, S):
    def dfs(current_pool, visited, available_pools):
        nonlocal orderAmount
        visited.add(current_pool)
        
        # Check if the sum of availability across all pools is already 0
        if sum(state["Availability"].values()) == 0:
            return
        
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
            print(min_pool)
            print(orderticket)
            print(orderAmount)

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
                print(pool)
                print(orderticket_pool)
                print(orderAmount)
        
        # Recursively call dfs on the next available pool
        for pool in available_neighbors:
            if pool not in visited:
                dfs(pool, visited, available_pools)

        if orderAmount == 0:
            return

    visited = set()
    starting_pools = list(G.keys())
    starting_pools.sort(key=lambda pool: action["AskPrice"][pool])  # Sort starting pools by ask prices
    dfs(starting_pools[0], visited, starting_pools)

    return [starting_pools]

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