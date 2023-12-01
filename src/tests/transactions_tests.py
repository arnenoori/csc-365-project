import pytest
from http.client import HTTPException
import sqlalchemy
from src.api.transactions import NewTransaction, create_transaction, update_transaction, check_transaction_query, db


class TestNewTransaction:

    # Creating a new transaction with valid merchant, description, and date
    def test_create_transaction_valid(self):
        transaction = NewTransaction(merchant="Amazon", description="Purchase", date="2022-01-01")
        result = create_transaction(1, transaction)
        assert result["transaction_id"] is not None

    # Updating an existing transaction with valid merchant, description, and date
    def test_update_transaction_valid1(self):
        transaction = NewTransaction(merchant="Amazon", description="Purchase", date="2022-01-01")
        result = update_transaction(1, 1, transaction)
        assert result["transaction_id"] == 1
        assert result["merchant"] == "Amazon"
        assert result["description"] == "Purchase"
        assert result["date"] == "2022-01-01"

    # Creating a new transaction with the minimum required fields (merchant, description, date)
    def test_create_transaction_minimum_fields(self):
        transaction = NewTransaction(merchant="Amazon", description="Purchase", date="2022-01-01")
        result = create_transaction(1, transaction)
        assert result["transaction_id"] is not None

    # Creating a new transaction with an empty merchant field
    def test_create_transaction_empty_merchant(self):
        transaction = NewTransaction(merchant="", description="Purchase", date="2022-01-01")
        with pytest.raises(HTTPException):
            create_transaction(1, transaction)

    # Updating an existing transaction with an empty merchant field
    def test_update_transaction_empty_merchant(self):
        transaction = NewTransaction(merchant="", description="Purchase", date="2022-01-01")
        with pytest.raises(HTTPException):
            update_transaction(1, 1, transaction)

    # Creating a new transaction with an empty description field
    def test_create_transaction_empty_description(self):
        transaction = NewTransaction(merchant="Amazon", description="", date="2022-01-01")
        with pytest.raises(HTTPException):
            create_transaction(1, transaction)

    # Creating a new transaction with a merchant and description that are the maximum allowed length
    def test_create_transaction_maximum_length(self):
        # Create a transaction with maximum allowed length for merchant and description
        transaction = NewTransaction(merchant="M" * 255, description="D" * 255, date="2022-01-01")
    
        # Call the create_transaction function
        result = create_transaction(1, transaction)
    
        # Assert that the transaction_id is not None
        assert result["transaction_id"] is not None

    # Updating an existing transaction with a merchant and description that are the maximum allowed length
    def test_update_transaction_max_length(self):
        # Create a transaction with maximum allowed length for merchant and description
        transaction = NewTransaction(merchant="M" * 255, description="D" * 255, date="2022-01-01")
        result = update_transaction(1, 1, transaction)
    
        # Check if the transaction is updated successfully
        assert result["transaction_id"] == 1
        assert result["merchant"] == "M" * 255
        assert result["description"] == "D" * 255
        assert result["date"] == "2022-01-01"

    # Updating an existing transaction with the minimum required fields (merchant, description, date)
    def test_update_transaction_valid2(self):
        # Create a new transaction
        transaction = NewTransaction(merchant="Amazon", description="Purchase", date="2022-01-01")
        result = create_transaction(1, transaction)
        transaction_id = result["transaction_id"]

        # Update the transaction
        updated_transaction = NewTransaction(merchant="eBay", description="Sale", date="2022-02-01")
        result = update_transaction(1, transaction_id, updated_transaction)

        # Check if the transaction is updated correctly
        assert result["transaction_id"] == transaction_id
        assert result["merchant"] == "eBay"
        assert result["description"] == "Sale"
        assert result["date"] == "2022-02-01"

    # Updating an existing transaction with a date in the format "YYYY-MM-DD"
    def test_update_transaction_valid_date(self):
        # Arrange
        user_id = 1
        transaction_id = 1
        transaction = NewTransaction(merchant="Amazon", description="Purchase", date="2022-01-01")

        # Act
        result = update_transaction(user_id, transaction_id, transaction)

        # Assert
        assert result["transaction_id"] == transaction_id
        assert result["merchant"] == transaction.merchant
        assert result["description"] == transaction.description
        assert result["date"] == transaction.date

    # Creating a new transaction with a date in the format "YYYY-MM-DD"
    def test_create_transaction_with_valid_date(self):
        transaction = NewTransaction(merchant="Amazon", description="Purchase", date="2022-01-01")
        result = create_transaction(1, transaction)
        assert result["transaction_id"] is not None

    # Creating a new transaction with an invalid date format
    def test_create_transaction_invalid_date_format(self):
        transaction = NewTransaction(merchant="Amazon", description="Purchase", date="2022/01/01")
        with pytest.raises(HTTPException) as exc_info:
            create_transaction(1, transaction)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid date"

    # Updating an existing transaction with an empty description field
    def test_update_transaction_empty_description(self):
        # Create a transaction with a non-empty description
        transaction = NewTransaction(merchant="Amazon", description="Purchase", date="2022-01-01")
        result = create_transaction(1, transaction)
        transaction_id = result["transaction_id"]

        # Update the transaction with an empty description
        updated_transaction = NewTransaction(merchant="Amazon", description="", date="2022-01-01")
        update_transaction(1, transaction_id, updated_transaction)

        # Retrieve the updated transaction from the database
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(check_transaction_query),
                [{"transaction_id": transaction_id, "user_id": 1}]).fetchone()

        # Assert that the description of the updated transaction is empty
        assert result.description == ""

    # Updating an existing transaction with an invalid date format
    def test_update_transaction_invalid_date_format(self):
        # Arrange
        user_id = 1
        transaction_id = 1
        transaction = NewTransaction(merchant="Amazon", description="Purchase", date="2022-01-01")
    
        # Act
        with pytest.raises(HTTPException) as exception:
            update_transaction(user_id, transaction_id, transaction)
    
        # Assert
        assert exception.value.status_code == 400
        assert exception.value.detail == "Invalid date"