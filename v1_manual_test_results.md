# Example Workflow

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

5. **Retrieve her transactions**
    ```json
    GET /user/{user_id}/transactions
    ```

6. **Retrieve her purchases**
    ```json
    GET /user/{user_id}/transactions/{transaction_id}/purchases
    ```


# Testing Results 