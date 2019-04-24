# Danger Log

1. Atomicity

   Some operations should be considered as a transaction, so that no operations will be executed if one of them fails. One example is when two orders matches, the engine should add balance to the seller and add symbols to the buyer.

2. Critical sections
    
    Database validation and execution should be encapsulated into transactions.

   ```
   # read from db
   Critical
   	# check the value from db
   	# branch1 : do stuff in db
   	# branch2 : do other stuff in db
   Critical
   ...
   ```

3. Asynchronous I/O
    
    For now, we are using synchronous I/O. However, asynchronous I/O should be a better approach for a more scalable solution.
    Python frameworks such as Tornado and Celery can provide more scalability. 