# API Specification

## 1. Instantiating a new user

### 1.1 Create User - '/user/' (POST)

Creates a new user.

**Request**:

```json
{
  "name": "string",
  "email": "string",
}
```

**Returns**:

```json
{
    "user_id": "integer"
}
```

## 2. Transactions

### 2.1 Get Transactions - '/user/{user_id}/transactions/' (GET)

Retrieves the transactions for a specified user.

**Returns**:

```json
[
    {
        "merchant": "string",
        "description": "string",
        "created_at": "datetime"
    }
]
```

### 2.2 Create Transaction - '/user/{user_id}/transactions/' (POST)

Creates a new transaction for a specified user.

**Request**:

```json
{
  "merchant": "string",
  "description": "string"
}
```

**Returns**:

```json
{
    "transaction_id": "integer"
}
```

## 3. Purchases

### 3.1 Get Purchases - '/user/{user_id}/transactions/{transaction_id}/purchases/' (GET)

Retrieves the purchases related to a specified transaction for a user.

**Returns**:

```json
[
    {
        "item": "string",
        "price": "float",
        "category": "string",
        "warranty_date": "date",
        "return_date": "date"
    }
]
```

### 3.2 Create Purchase - '/user/{user_id}/transactions/{transaction_id}/purchases/' (POST)

Creates a new purchase record for a specific transaction of a user.

**Request**:

```json
{
  "item": "string",
  "price": "float",
  "category": "string",
  "warranty_date": "date",
  "return_date": "date"
}
```

**Returns**: 
```json
{
    "purchase_id": "integer"
}
```
