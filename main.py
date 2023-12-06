#Main Function
#Group 1 
#Date: 10/15/2023
from matplotlib import *
import matplotlib.pyplot as plt
import networkx as nx
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

    # Create a directed graph
    G_plot = nx.DiGraph(G)

    # Set node attributes (ask prices and availability)
    nx.set_node_attributes(G_plot, askprices, 'askprices')
    nx.set_node_attributes(G_plot, availability, 'availability')

    # Set edge attributes (slippages)
    nx.set_edge_attributes(G_plot, S, 'slippages')

    # Draw the graph
    pos = nx.spring_layout(G_plot)  # You can use different layout algorithms
    nx.draw(G_plot, pos, with_labels=True, font_weight='bold', node_size=700, node_color='skyblue', font_color='black')

    # Draw edge labels (slippages)
    edge_labels = {(i, j): f"{S[(i, j)]}" for i, j in G_plot.edges()}
    nx.draw_networkx_edge_labels(G_plot, pos, edge_labels=edge_labels)

    # Draw node attributes (ask prices and availability)
    node_attributes = {node: f"{askprices[node]}\n{availability[node]}" for node in G_plot.nodes()}
    nx.draw_networkx_labels(G_plot, pos, labels=node_attributes)

    plt.show()

    totalCost = FIOR(G, state, action, orderID, orderLog, orderAmount, starting_pool, S)
    print(totalCost)
    
    
if __name__ == "__main__":
    main()