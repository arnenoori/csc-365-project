# V5 - Performane Tuning

## Fake Data Modeling

Link to python file used to construct the million rows of data: 

### Tables
Users - 60,000 rows
Purchases - 376,349 rows
Budgets - 60,000 rows
Transactions - 150,087 rows

This code generates 1,039,209 rows in total

This simulated data is in line with how we predict the data in our application would scale in a real world scenario. We simulated with 8,000 users. Each user has 5-10 transactions and each transaction has 5-30 purchases. Additionally, each user has 1 budget. A transaction is defined as a shopping event while a purchase is an an individual purchase during this shopping event. 

## Performance Results of Hitting Endpoints

### Execution time of each endpoint

1. GET - Get Purchase Categorized by Transaction - 62ms
2. GET - Get Transactions - 94ms
3. POST - Create Transaction - 11ms
4. PUT - Update Transaction - 13ms
5. DELETE - Delete Transaction - 66ms
6. POST - Create User - 53ms
7. GET - Get User - 2ms
8. PUT - Update User - 15ms
9. DELETE - Delete User - 616ms
10. GET - Get all Purchases Categorized - 139ms
11. GET - Get all Purchases Warranty - 612ms
12. GET - Get Purchases - 744ms
13. POST - Create Purchase - 55ms
14. PUT - Update Purchase - 56ms
15. DELETE - Delete Purchase - 4ms
16. GET - Get Budgets - 6ms
17. POST - Create Budget - 50ms
18. PUT - Update Budget - 10ms
19. GET - Compare Budgets to Actual Spending - 65ms
20. GET - Get All Purchases Categorized - 78ms

### Three slowest endpoints

2. GET - Get Transactions - 94ms
11. GET - Get all Purchases Warranty - 612ms
12. GET - Get Purchases - 744ms

We are skipping 'GET - Get All Purchases Categorized' since this GET call already goes through every purchase. It cannot be optimized. Also, we are disregarding the DELETE since this delete call already finds users by their IDs which is already an index.

## Performance Tuning

### Slow Endpoint \#1 - GET - Get Transactions

- results of running explain:

- describe what this explain means to you and what index you will add to speed up your query

- Command for adding the index:

- New explain results

- did this have the expected results

- continue until acceptably fast


### Slow Endpoint \#2 - GET - Get All Purchases Warranty


### Slow Endpoint \#3 - GET - Get Purchases
