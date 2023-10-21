# API Example Flows

## Example Flow 1: User Logs a Purchase

**Scenario:** Alice wants to manually log her purchases to maintain a detailed record.

1. **Authenticate the user**
    ```json
    POST /auth/signin
    {
      "email": "alice@example.com",
      "password": "securepassword123"
    }
    ```

2. **Manually add a purchase**
    ```json
    POST /purchase
    {
      "item_name": "Groceries",
      "amount": 25.50,
      "category": "Food",
      "date": "2023-10-22"
    }
    ```

3. **Upload a receipt image**
    ```json
    POST /receipt
    {
      "image": "image.jpg",
      "purchase_id": 1
    }
    ```

4. **Retrieve the latest purchase**
    ```json
    GET /purchase?latest=true
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
