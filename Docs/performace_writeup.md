# V5 - Performane Tuning

## Fake Data Modeling

Link to python file used to construct the million rows of data: 

### Tables
Users - **8,000 rows**
Purchases - **962,891 rows**
Budgets - **8,000 rows**
Transactions - **46,432 rows**

This code generates **1,025,323 rows** in total

This simulated data is in line with how we predict the data in our application would scale in a real world scenario. We simulated with 8,000 users. Each user has 5-10 transactions and each transaction has 5-30 purchases. Additionally, each user has 1 budget. A transaction is defined as a shopping event while a purchase is an an individual purchase during this shopping event. 

## Performance Results of Hitting Endpoints

### Execution time of each endpoint

1. `GET` - Get Purchase Categorized by Transaction - **62ms**
2. `GET` - Get Transactions - **94ms**
3. `POST` - Create Transaction - **11ms**
4. `PUT` - Update Transaction - **13ms**
5. `DELETE` - Delete Transaction - **66ms**
6. `POST` - Create User - **53ms**
7. `GET` - Get User - **2ms**
8. `PUT` - Update User - **15ms**
9. `DELETE` - Delete User - **616ms**
10. `GET` - Get all Purchases Categorized - **139ms**
11. `GET` - Get all Purchases Warranty - **612ms**
12. `GET` - Get Purchases - **744ms**
13. `POST` - Create Purchase - **55ms**
14. `PUT` - Update Purchase - **56ms**
15. `DELETE` - Delete Purchase - **4ms**
16. `GET` - Get Budgets - **6ms**
17. `POST` - Create Budget - **50ms**
18. `PUT` - Update Budget - **10ms**
19. `GET` - Compare Budgets to Actual Spending - **65ms**
20. `GET` - Get All Purchases Categorized - **78ms**

### Three slowest endpoints

2. `GET` - Get Transactions - **94ms**
11. `GET` - Get all Purchases Warranty - **612ms**
12. `GET` - Get Purchases - **744ms**

We are skipping '`GET` - Get All Purchases Categorized' since this `GET` call already goes through every purchase. It cannot be optimized. Also, we are disregarding the `DELETE` since this `DELETE` call finds users by their IDs which is already an index.

## Performance Tuning

### Slow Endpoint \#1 - GET - Get Transactions

- initial results of running explain analyze:
```sql
QUERY PLAN                                                                                                                         |
-----------------------------------------------------------------------------------------------------------------------------------+
Limit  (cost=2043.47..2043.48 rows=1 width=82) (actual time=64.437..64.438 rows=0 loops=1)                                         |
  ->  Sort  (cost=2043.47..2043.48 rows=1 width=82) (actual time=64.436..64.437 rows=0 loops=1)                                    |
        Sort Key: date                                                                                                             |
        Sort Method: quicksort  Memory: 25kB                                                                                       |
        ->  Seq Scan on transactions  (cost=0.00..2043.46 rows=1 width=82) (actual time=64.429..64.430 rows=0 loops=1)             |
              Filter: ((date >= '2023-1-01'::text) AND (date <= '2023-12-12'::text) AND (merchant ~~* '%'::text) AND (user_id = 3))|
              Rows Removed by Filter: 55923                                                                                        |
Planning Time: 0.554 ms                                                                                                            |
Execution Time: 64.463 ms                                                                                                           |
```

- This query plan indicates that the query performs a sequential scan on the transactions tabe, filtering records based on date, merchant, and user_id, followed by sorting on the date column. To speed up this query, we will add an index to the date column. 

- Command for adding the index:
```SQL
create index tdate on transactions (date)
```

- New explain analyze results:
```json
QUERY PLAN                                                                                                                      |
--------------------------------------------------------------------------------------------------------------------------------+
Limit  (cost=1402.67..1402.67 rows=1 width=82) (actual time=26.191..26.192 rows=0 loops=1)                                      |
  ->  Sort  (cost=1402.67..1402.67 rows=1 width=82) (actual time=26.189..26.190 rows=0 loops=1)                                 |
        Sort Key: date                                                                                                          |
        Sort Method: quicksort  Memory: 25kB                                                                                    |
        ->  Bitmap Heap Scan on transactions  (cost=287.50..1402.66 rows=1 width=82) (actual time=26.182..26.182 rows=0 loops=1)|
              Recheck Cond: ((date >= '2023-1-01'::text) AND (date <= '2023-12-12'::text))                                      |
              Filter: ((merchant ~~* '%'::text) AND (user_id = 3))                                                              |
              Rows Removed by Filter: 9626                                                                                      |
              Heap Blocks: exact=925                                                                                            |
              ->  Bitmap Index Scan on tdate  (cost=0.00..287.50 rows=9508 width=0) (actual time=8.367..8.367 rows=9626 loops=1)|
                    Index Cond: ((date >= '2023-1-01'::text) AND (date <= '2023-12-12'::text))                                  |
Planning Time: 0.870 ms                                                                                                         |
Execution Time: 26.328 ms    
```

- Yes, this had the expected result. With this added index, the query is now acceptably fast.  


### Slow Endpoint \#2 - GET - Get All Purchases Warranty

- initial results of running explain analyze:
```sql
QUERY PLAN                                                                                                                             |
---------------------------------------------------------------------------------------------------------------------------------------+
Nested Loop  (cost=18667.50..20291.72 rows=7 width=17) (actual time=256.664..266.135 rows=0 loops=1)                                   |
  ->  Gather Merge  (cost=18667.50..18667.62 rows=1 width=17) (actual time=256.663..266.132 rows=0 loops=1)                            |
        Workers Planned: 2                                                                                                             |
        Workers Launched: 2                                                                                                            |
        ->  Sort  (cost=17667.47..17667.48 rows=1 width=17) (actual time=222.308..222.308 rows=0 loops=3)                              |
              Sort Key: p.warranty_date                                                                                                |
              Sort Method: quicksort  Memory: 25kB                                                                                     |
              Worker 0:  Sort Method: quicksort  Memory: 25kB                                                                          |
              Worker 1:  Sort Method: quicksort  Memory: 25kB                                                                          |
              ->  Parallel Seq Scan on purchases p  (cost=0.00..17667.46 rows=1 width=17) (actual time=222.211..222.211 rows=0 loops=3)|
                    Filter: ((warranty_date <= '2023-12-09'::text) AND (transaction_id = 2))                                           |
                    Rows Removed by Filter: 317884                                                                                     |
  ->  Seq Scan on transactions t  (cost=0.00..1624.04 rows=7 width=0) (never executed)                                                 |
        Filter: (user_id = 1)                                                                                                          |
Planning Time: 0.912 ms                                                                                                                |
Execution Time: 266.191 ms 
```

- This query plan indicates that the query begins with a sequential sacn on the purchases table, filtering based on warranty_date and transaction_id, followed by a sequential scan on transaction table, filtering by user_id. To speed up this query, we will add an index to warranty_datye in the purchases table.

- Command for adding the index:
```sql
create index pwarranty on purchases (warranty_date)
```

- New explain analyze results:
```sql
QUERY PLAN                                                                                                                      |
--------------------------------------------------------------------------------------------------------------------------------+
Sort  (cost=14297.05..14297.06 rows=7 width=17) (actual time=45.659..45.660 rows=0 loops=1)                                     |
  Sort Key: p.warranty_date                                                                                                     |
  Sort Method: quicksort  Memory: 25kB                                                                                          |
  ->  Nested Loop  (cost=209.96..14296.95 rows=7 width=17) (actual time=45.649..45.650 rows=0 loops=1)                          |
        ->  Bitmap Heap Scan on purchases p  (cost=209.96..12672.84 rows=1 width=17) (actual time=45.648..45.648 rows=0 loops=1)|
              Recheck Cond: (warranty_date <= '2023-12-09'::text)                                                               |
              Filter: (transaction_id = 2)                                                                                      |
              Rows Removed by Filter: 20831                                                                                     |
              Heap Blocks: exact=9749                                                                                           |
              ->  Bitmap Index Scan on a  (cost=0.00..209.96 rows=18871 width=0) (actual time=5.064..5.064 rows=20831 loops=1)  |
                    Index Cond: (warranty_date <= '2023-12-09'::text)                                                           |
        ->  Seq Scan on transactions t  (cost=0.00..1624.04 rows=7 width=0) (never executed)                                    |
              Filter: (user_id = 1)                                                                                             |
Planning Time: 0.650 ms                                                                                                         |
Execution Time: 46.503 ms 
```

- Yes, this had the expected result. With this added index, the query is now acceptably fast.   


### Slow Endpoint \#3 - GET - Get Purchases

- Initial results of running explain analyze:
```sql
QUERY PLAN                                                                                                                                      |
------------------------------------------------------------------------------------------------------------------------------------------------+
Gather Merge  (cost=23270.63..23271.33 rows=6 width=78) (actual time=1007.148..1015.855 rows=0 loops=1)                                         |
  Workers Planned: 2                                                                                                                            |
  Workers Launched: 2                                                                                                                           |
  ->  Sort  (cost=22270.61..22270.62 rows=3 width=78) (actual time=971.057..971.062 rows=0 loops=3)                                             |
        Sort Key: transactions.date                                                                                                             |
        Sort Method: quicksort  Memory: 25kB                                                                                                    |
        Worker 0:  Sort Method: quicksort  Memory: 25kB                                                                                         |
        Worker 1:  Sort Method: quicksort  Memory: 25kB                                                                                         |
        ->  Nested Loop  (cost=0.00..22270.59 rows=3 width=78) (actual time=970.923..970.928 rows=0 loops=3)                                    |
              ->  Parallel Seq Scan on purchases  (cost=0.00..20646.48 rows=1 width=58) (actual time=970.922..970.926 rows=0 loops=3)           |
                    Filter: ((item ~~* '%'::text) AND (category ~~* '%'::text) AND (price >= 100) AND (price <= 1000) AND (transaction_id = 11))|
                    Rows Removed by Filter: 317884                                                                                              |
              ->  Seq Scan on transactions  (cost=0.00..1624.04 rows=7 width=20) (never executed)                                               |
                    Filter: (user_id = 2)                                                                                                       |
Planning Time: 0.355 ms                                                                                                                         |
Execution Time: 1015.893 ms                                                                                                                     |                                                
```

- This query plan indicates that the query executes a squential scan on the purchases table with filters on item, category, price, and transaction_id, followed by a sequential scan on the transactions table, filtered by user_id. To speed up this query, we will add an index on the price column in the purchases table. 

- Command for adding the index:
```sql
create index ppurchase on purchases (price)
```

- New explain analyze results:
```sql
QUERY PLAN                                                                                                                      |
--------------------------------------------------------------------------------------------------------------------------------+
Sort  (cost=1632.66..1632.68 rows=7 width=78) (actual time=0.024..0.025 rows=0 loops=1)                                         |
  Sort Key: transactions.date                                                                                                   |
  Sort Method: quicksort  Memory: 25kB                                                                                          |
  ->  Nested Loop  (cost=0.42..1632.56 rows=7 width=78) (actual time=0.020..0.020 rows=0 loops=1)                               |
        ->  Index Scan using ppurchase on purchases  (cost=0.42..8.45 rows=1 width=58) (actual time=0.019..0.019 rows=0 loops=1)|
              Index Cond: ((price >= 100) AND (price <= 1000))                                                                  |
              Filter: ((item ~~* '%'::text) AND (category ~~* '%'::text) AND (transaction_id = 11))                             |
        ->  Seq Scan on transactions  (cost=0.00..1624.04 rows=7 width=20) (never executed)                                     |
              Filter: (user_id = 2)                                                                                             |
Planning Time: 0.257 ms                                                                                                         |
Execution Time: 0.052 ms                                                                                                        |
                                                                                                 |
```

- Yes, this had the expected result. With this added index, the query is now acceptably fast. 
