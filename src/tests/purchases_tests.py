import pytest
from http.client import HTTPException
from src.api.budget import NewPurchase, create_purchase


class TestNewPurchase:

    # Creating a new purchase with valid inputs should be successful.
    def test_create_purchase_with_valid_inputs1(self):
        purchase = NewPurchase(
            item="Item",
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        result = create_purchase(1, 1, purchase)
        assert "purchase_id" in result

    # Creating a new purchase with the minimum valid inputs should be successful.
    def test_create_purchase_with_minimum_valid_inputs(self):
        purchase = NewPurchase(
            item="Item",
            price=1,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        result = create_purchase(1, 1, purchase)
        assert "purchase_id" in result

    # Creating a new purchase with the maximum valid inputs should be successful.
    def test_create_purchase_with_maximum_valid_inputs(self):
        purchase = NewPurchase(
            item="Item" * 25,
            price=1000000,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=100
        )
        result = create_purchase(1, 1, purchase)
        assert "purchase_id" in result

    # Creating a new purchase with an empty item should raise a validation error.
    def test_create_purchase_with_empty_item(self):
        purchase = NewPurchase(
            item="",
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        with pytest.raises(HTTPException):
            create_purchase(1, 1, purchase)

    # Creating a new purchase with an item longer than 100 characters should raise a validation error.
    def test_create_purchase_with_long_item(self):
        purchase = NewPurchase(
            item="Item" * 26,
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        with pytest.raises(HTTPException):
            create_purchase(1, 1, purchase)

    # Creating a new purchase with a negative price should raise a validation error.
    def test_create_purchase_with_negative_price(self):
        purchase = NewPurchase(
            item="Item",
            price=-10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        with pytest.raises(HTTPException):
            create_purchase(1, 1, purchase)

    # Creating a new purchase with the same minimum and maximum valid inputs should be successful.
    def test_create_purchase_with_valid_inputs2(self):
        purchase = NewPurchase(
            item="Item",
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        result = create_purchase(1, 1, purchase)
        assert "purchase_id" in result

    # Creating a new purchase with the same valid inputs as an existing purchase, but with different category should be successful.
    def test_create_purchase_with_different_category(self):
        # Create an existing purchase
        existing_purchase = NewPurchase(
            item="Item",
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        existing_purchase_result = create_purchase(1, 1, existing_purchase)
        existing_purchase_id = existing_purchase_result["purchase_id"]

        # Create a new purchase with the same inputs but different category
        new_purchase = NewPurchase(
            item="Item",
            price=10,
            category="Electronics",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        new_purchase_result = create_purchase(1, 1, new_purchase)
        new_purchase_id = new_purchase_result["purchase_id"]

        # Assert that the new purchase is created successfully
        assert new_purchase_id != existing_purchase_id

    # Creating a new purchase with the same valid inputs as an existing purchase, but with different transaction_id should be successful.
    def test_create_purchase_with_same_valid_inputs_different_transaction_id(self):
        # Create an existing purchase
        existing_purchase = NewPurchase(
            item="Item",
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        create_purchase(1, 1, existing_purchase)

        # Create a new purchase with the same valid inputs but different transaction_id
        new_purchase = NewPurchase(
            item="Item",
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        result = create_purchase(1, 2, new_purchase)

        assert "purchase_id" in result

    # Creating a new purchase with the same valid inputs as an existing purchase, but with different quantity should be successful.
    def test_create_purchase_with_different_quantity(self):
        # Create an existing purchase
        existing_purchase = NewPurchase(
            item="Item",
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        existing_purchase_result = create_purchase(1, 1, existing_purchase)
        existing_purchase_id = existing_purchase_result["purchase_id"]

        # Create a new purchase with different quantity
        new_purchase = NewPurchase(
            item="Item",
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=2
        )
        new_purchase_result = create_purchase(1, 1, new_purchase)
        new_purchase_id = new_purchase_result["purchase_id"]

        # Assert that the new purchase is created successfully
        assert new_purchase_id != existing_purchase_id

    # Creating a new purchase with the same valid inputs as an existing purchase should be successful.
    def test_create_purchase_with_same_valid_inputs(self):
        # Create a new purchase with valid inputs
        purchase = NewPurchase(
            item="Item",
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        result = create_purchase(1, 1, purchase)
        assert "purchase_id" in result

        # Create a new purchase with the same valid inputs as the existing purchase
        result = create_purchase(1, 1, purchase)
        assert "purchase_id" in result

    # Creating a new purchase with the same valid inputs as an existing purchase, but with different user_id should be successful.
    def test_create_purchase_with_different_user_id(self):
        # Create an existing purchase
        existing_purchase = NewPurchase(
            item="Item",
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        create_purchase(1, 1, existing_purchase)

        # Create a new purchase with the same inputs but different user_id
        new_purchase = NewPurchase(
            item="Item",
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        result = create_purchase(2, 1, new_purchase)

        # Assert that the new purchase was created successfully
        assert "purchase_id" in result

    # Creating a new purchase with the same valid inputs as an existing purchase, but with different price should be successful.
    def test_create_purchase_with_different_price(self):
        # Create an existing purchase
        existing_purchase = NewPurchase(
            item="Item",
            price=10,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        existing_purchase_result = create_purchase(1, 1, existing_purchase)
        existing_purchase_id = existing_purchase_result["purchase_id"]

        # Create a new purchase with different price
        new_purchase = NewPurchase(
            item="Item",
            price=20,
            category="Groceries",
            warranty_date="2022-01-01",
            return_date="2022-02-01",
            quantity=1
        )
        new_purchase_result = create_purchase(1, 1, new_purchase)
        new_purchase_id = new_purchase_result["purchase_id"]

        # Assert that the new purchase is created successfully
        assert new_purchase_id != existing_purchase_id