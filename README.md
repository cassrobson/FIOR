# FIOR
Smart Order Routing for Fixed Income Securities using Markov Decision Process
Below you will see the output of the FIOR_LPOptimization.py file, this takes an Markov Decision Process model of a Graph which represents pools of liquidity linked by exchange, with states and actions defined as well. In the repository, another approach to the FIOR implementation was using DFS traversal, which is attached and follows a similar structure which differs in that it does not us linear programming or optimization to solve the MDP. 

![FIOR](https://github.com/cassrobson/FIOR/assets/116671665/ad41e2e5-7a0b-4ae0-bef5-77e77f80fa5f)

-----------------ORDER INITIALIZED------------------
We are about to commance the smart order routing process (MDP) using linear programming and optimization for:  120   MSFT CRP BONDS
We will begin at pool --> A
Previous Node:  A
Currently at node:  A
All direct neighbors -->  ['B', 'C', 'E']
All direct neighbors with bonds available -->  ['E']
Ask prices of direct neighbors with bonds available -->  [100.1]
-----------------------------------------------------------------
Previous Node:  A
Currently at node:  E
All direct neighbors -->  ['D', 'B', 'A']
All direct neighbors with bonds available -->  ['D', 'A']
Ask prices of direct neighbors with bonds available -->  [100.2, 100.4]
-----------------------------------------------------------------
Previous Node:  E
Currently at node:  A
All direct neighbors -->  ['B', 'C', 'E']
All direct neighbors with bonds available -->  []
Ask prices of direct neighbors with bonds available -->  []
-----------------------------------------------------------------
Previous Node:  A
Currently at node:  E
All direct neighbors -->  ['D', 'B', 'A']
All direct neighbors with bonds available -->  ['D']
Ask prices of direct neighbors with bonds available -->  [100.2]
-----------------------------------------------------------------
Previous Node:  E
Currently at node:  D
All direct neighbors -->  ['C', 'E']
All direct neighbors with bonds available -->  []
Ask prices of direct neighbors with bonds available -->  []
-----------------------------------------------------------------
Finished at node: D We have reached the exhaustion state
Amount spent at pool  D  is:  5010.0
Number of bonds purchased at  D  is:  110
Number of bonds remaining in order is:  10
Current total cost of the order -->  11022.0

-----------------Exhaustion State--------------------
--------This means that there remain no pools with bonds available at their original price----------
------Here is when slippage takes affect on the price of market orders--------

Remaining number of bonds to buy as market orders -->  10
We are currently at pool -->  D
Minimum accessible slippage route identified -->  0.5   ('D', 'E')
Remaining number of bonds purchased at pool  E  with slippage cost of  5.004999999999882

-------REWARD CALCULATION--------
We successfully fulfilled the customers order -> +1
We successfully kept slippage cost to under 2 percent of the total cost of the order -> +1
Our total cost for the order failed to fall below the cost of buying the bonds at an average ask price -> -1

-------SUMMARY OF ORDER EXECUTION----------

Slippage Exchange Route:  [('D', 'E')] Total Cost of entire order:  12028.005 Slippage Cost:  5.004999999999882
('Pools visited -->', [{'A', 'D', 'E'}], ' --> ', ('OVERALL REWARD --> ', 1))
