# API Example Flows

## Example Flow 1: User Logs a Purchase

**Scenario:** Alice wants to sign up and log her first purchases.

1. **Instantiate the user**
    ```json
    POST /user
    {
      "name": "Alice",
      "email": "alice@example.com"
    }
    ```

2. **Manually add a transaction**
    ```json
    POST /user/{user_id}/transactions
    {
      "merchant": "Amazon",
      "description": "Book Purchase"
    }
    ```

3. **Manually add another transaction**
    ```json
    POST /user/{user_id}/transactions
    {
      "merchant": "Walmart",
      "description": "Groceries"
    }
    ```

4. **Manually add a purchase**
    ```json
    POST /user/{user_id}/transactions/{transaction_id}/purchases
    {
      "item": "Novel",
      "price": 15.99,
      "category": "Books",
      "warranty_date": "2025-05-01",
      "return_date": "2023-12-15"
    }
    ```

4. **Retrieve her transactions**
    ```json
    GET /user/{user_id}/transactions
    ```

5. **Retrieve her purchases**
    ```json
    GET /user/{user_id}/transactions/{transaction_id}/purchases
    ```

## Example Flow 2: User Reviews Purchase History

**Scenario:** Bob wants to review his purchase history and update his financial goals.

1. **Authenticate the user**
    ```json
    POST /auth/signin
    {
      "email": "bob@example.com",
      "password": "bobpassword456"
    }
    ```

2. **Set a new financial goal**
    ```json
    POST /goal
    {
      "goal": "Save for vacation",
      "amount": 2000,
      "deadline": "2024-05-01"
    }
    ```

3. **Retrieve purchase history**
    ```json
    GET /purchase
    ```

4. **Retrieve financial goals**
    ```json
    GET /goal
    ```

5. **Update a financial goal**
    ```json
    PUT /goal/{goalId}
    {
      "amount": 2500
    }
    ```

## Example Flow 3: User Seeks Financial Advice

**Scenario:** Charlie wants to receive budgeting advice and visualize his financial data.

1. **Authenticate the user**
    ```json
    POST /auth/signin
    {
      "email": "charlie@example.com",
      "password": "charliesecure789"
    }
    ```

2. **Ask for budgeting advice**
    ```json
    GET /recommendations
    ```

3. **Visualize financial data**
    ```json
    GET /dashboard
    ```

4. **Export financial data**
    ```json
    GET /export?format=pdf
    ```

---
