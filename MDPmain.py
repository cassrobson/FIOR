#Main Function
#Group 1 
#Date: 10/15/2023
from matplotlib import *
import matplotlib.pyplot as plt
import networkx as nx
from FIOR_LPOptimization import *
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
        ('A', 'C'): 2,
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
    orderID = "MSFT CRP BONDS"
    orderAmount = 120

    state = {
        "CurrentPool": starting_pool,
        "RemainingOrderAmount": orderAmount,
        "Availability": availability,
        "AskPrice": askprices,
        "Slippages": S
    }
    action = {
        "AvailablePools": list(G.keys()),
    }
    
    G_plot = nx.DiGraph()

    G_plot.add_nodes_from(G.keys())

    for (source, target), slippage in S.items():
        G_plot.add_edge(source, target, slippage=slippage)

    nx.set_node_attributes(G_plot, askprices, 'askprices')
    nx.set_node_attributes(G_plot, availability, 'availability')
    
    nx.set_edge_attributes(G_plot, S, "slippage")

    # Node color based on availability
    node_colors = ['red' if availability[node] == 0 else 'green' for node in G_plot.nodes()]

    fig, ax = plt.subplots(figsize=(8, 6))
    pos = nx.spring_layout(G_plot, seed=42, k=0.15, iterations=50)
    nx.draw(G_plot, pos, with_labels=True, font_weight='bold', node_size=700, node_color=node_colors, font_color='black',
        connectionstyle="arc3,rad=0.1")

    

    node_attributes = {node: f"Availability: {availability[node]}\nAsk Price: {askprices[node]}" for node in
                       G_plot.nodes()}
    
    # Move the labels outward
    pos_attributes = {k: (v[0], v[1] + 0.05) for k, v in pos.items()}
    
    nx.draw_networkx_labels(G_plot, pos_attributes, labels=node_attributes, font_size=8)

    # Display slippage values on the edges
    slippage_labels = {(source, target): f"Slippage: {slippage}" for (source, target, slippage) in
                       G_plot.edges(data='slippage')}
    nx.draw_networkx_edge_labels(G_plot, pos, edge_labels=slippage_labels, font_color='red', font_size=8)
    
    plt.show()
    
        
    
    totalcost = 0
    order = FIOR_LP(G, state, action, orderID, orderLog, orderAmount, starting_pool, S, totalcost)
    print(order)
    
    
if __name__ == "__main__":
    main()