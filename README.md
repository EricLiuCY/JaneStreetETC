Jane Street Eletronic Trading Competition


Members: Eric Liu, Felix He, Shivansh Vij:


Code Flow:

1. Connection, receive data from server
2. Parse from universal parser
3. Pass parsed info into a decision dispatcher
4. Take the returned the decision and pass to JSON generator
5. JSON generator sends JSON over to be sent to server. 
- C



BOND : [BUY, SELL, EMA]