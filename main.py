#Main Function
#Group 1 
#Date: 10/15/2023
from matplotlib import *
import matplotlib.pyplot as plt
from FIOR import *
def main():
    #structure of Pools
    G = {
        'A': ['B', 'C', 'E'],
        'B': ['A', 'E'],
        'C': ['A', 'D'],
        'D': ['C', 'E'],
        'E': ['D', 'B', 'A'],  
    }
    # slippages
    S = {
        ('A', 'B'): 2,
        ('B', 'A'): 3,
        ('A', 'C'): -2,
        ('C', 'A'): 4,
        ('A', 'E'): 3,
        ('E', 'A'): 4,
        ('B', 'E'): 8,
        ('E', 'B'): 1,
        ('D', 'E'): 0.5,
        ('E', 'D'): 2,
        ('D', 'C'): 1,
        ('C', 'D'): 7,
    }
    # askprices at each pool
    askprices = {
        "A": 100.40,
        "B": 0, 
        "C": 0, 
        "D": 100.20, 
        "E": 100.10 
        
    }
    availability = {
        "A": 20,
        "B": 0, 
        "C": 0, 
        "D": 50,
        "E": 40
    }
    

    E = [i for i in askprices if askprices[i] == None] #list of unavailable pools
    starting_pool = "A"
    A = []  # Traversed node list
    orderLog = {}
    orderID = "120 MSFT CRP BONDS"
    orderAmount = 120

    state = {
        "OrderVolume": orderAmount,
        "Availability": availability
    }
    action = {
        "AskPrice": askprices,
        #"SlippageDecision": SlippageDecision
    }

    # Create a plot
    plt.figure(figsize=(10, 8))

    # Draw nodes
    for node, pos in zip(G.keys(), [(0, 0), (1, 1), (1, -1), (2, 0), (3, 0)]):
        plt.scatter(*pos, s=500, label=f'{node}\nAsk: {askprices[node]}\nAvailability: {availability[node]}', edgecolors='black', linewidths=1, alpha=0.7)

    # Draw edges
    for edge, weight in S.items():
        plt.plot([*zip(*[(pos[0], pos[1]) for pos in [(0, 0), (1, 1), (1, -1), (2, 0), (3, 0)]][list(G.keys()).index(edge[0]), list(G.keys()).index(edge[1])])], linewidth=weight / 2, alpha=0.7)

    plt.legend()
    plt.show()

    totalCost = FIOR(G, state, action, orderID, orderLog, orderAmount, starting_pool, S)
    print(totalCost)
    
    
if __name__ == "__main__":
    main()