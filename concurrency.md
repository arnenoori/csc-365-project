Phenomena Without Concurrency Control
1. Dirty Reads

Might occur when:

- Transaction 1 (T1): User 1 uploads a receipt.
- Transaction 2 (T2): User 2 reads the receipt data before T1 commits.

If T1 rolls back, T2 would have read uncommitted data, leading to a dirty read.

Sequence diagram:
User 1->Service: Upload receipt (T1 starts)
Service->Database: Write receipt data
User 2->Service: Read receipt data (T2 starts)
Service->Database: Read receipt data
Service-->User 2: Return receipt data
Service->Database: Rollback T1 (T1 ends)

2. Non-Repeatable Reads

Might occur when:

- Transaction 1 (T1): User 1 reads receipt data.
- Transaction 2 (T2): User 2 updates the same receipt data.
- Transaction 1 (T1): User 1 reads the same receipt data again and gets different data.

Sequence diagram:
User 1->Service: Read receipt data (T1 starts)
Service->Database: Read receipt data
Service-->User 1: Return receipt data
User 2->Service: Update receipt data (T2 starts)
Service->Database: Update receipt data
Service->Database: Commit T2 (T2 ends)
User 1->Service: Read receipt data
Service->Database: Read receipt data
Service-->User 1: Return updated receipt data


3. Phantom Reads

Might occur when:

- Transaction 1 (T1): User 1 reads all receipts with a certain condition.
- Transaction 2 (T2): User 2 inserts a new receipt that satisfies the same condition.
- Transaction 1 (T1): User 1 reads all receipts with the same condition again and gets an additional receipt.

Sequence diagram:
User 1->Service: Read receipts with condition (T1 starts)
Service->Databaseundefined Read receipts with condition
Service-->User 1: Return receipts
User 2->Service: Insert new receipt (T2 starts)
Service->Database: Insert new receipt
Service->Database: Commit T2 (T2 ends)
User 1->Service: Read receipts with condition
Service->Database: Read receipts with condition
Service-->User 1: Return receipts including new receipt

### Concurrency Control Mechanisms

To prevent these phenomena, we will use the following concurrency control mechanisms:

- Transaction Isolation Levels: We will set the transaction isolation level to SERIALIZABLE, the highest level of isolation. Meaning that each transaction will be fully completed before the next transaction begins.

- Locking: We will use locks to prevent multiple transactions from accessing the same data concurrently. When a transaction is processing a piece of data, that data will be locked until the transaction is completed, preventing other transactions from accessing it

- Atomicity: If a transaction is interrupted (for example, due to an error), all changes made in that transaction will be rolled back, ensuring that the database remains in a consistent state.
