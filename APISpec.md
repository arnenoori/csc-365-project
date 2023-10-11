# API Reciepts App

## 1. Customer Purchasing

### 1.1. Sign Up - `/auth/signup` (POST)

Registers a new user with an email and password.

**Request**:

json
{
"email": "string",
"password": "string"
}


### 1.2. Sign In - `/auth/signin` (POST)

Authenticates a user and returns a token.

**Request**:

json
{
"email": "string",
"password": "string"
}


## 2. Dashboard

### 2.1. Get Dashboard - `/dashboard` (GET)

Retrieves the summary and graphical data for a user's financial status.

## 3. Purchase

### 3.1. Add Purchase - `/purchase` (POST)

Adds a new purchase record for a user.

**Request**:

json
{
"item_name": "string",
"price": "number",
"category": "string",
"store_name": "string",
"date": "string" / In ISO 8601 format /
}


### 3.2. Get Purchases - `/purchase` (GET)

Retrieves all purchase records for a user.

## 4. Receipt

### 4.1. Add Receipt - `/receipt` (POST)

Adds a new receipt record for a user.

**Request**:

json
{
"image": "string" / Base64 encoded image data /
}


### 4.2. Get Receipts - `/receipt` (GET)

Retrieves all receipt records for a user.

## 5. Financial Goals

### 5.1. Add Goal - `/goal` (POST)

Adds a new financial goal for a user.

**Request**:

json
{
"goal": "string",
"progress": "number"
}

### 5.2. Get Goals - `/goal` (GET)

Retrieves all financial goals for a user.

## 6. Budget Recommendations

### 6.1. Get Recommendations - `/recommendations` (GET)

Retrieves custom budget advice for a user based on their spending habits.

## 7. Export Data

### 7.1. Export Data - `/export` (GET)

Exports the user's financial data in various formats.

**Query Parameters**:

json
{
"format": "string" / One of 'pdf', 'csv', etc. /
}