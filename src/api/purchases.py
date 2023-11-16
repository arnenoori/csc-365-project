from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError, NoResultFound
from datetime import datetime
from fastapi import HTTPException

router = APIRouter(
    prefix="/user/{user_id}/transactions/{transaction_id}/purchases",
    tags=["purchase"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewPurchase(BaseModel):
    item: str
    price: int
    category: str
    warranty_date: str
    return_date: str
    quantity: int

def is_valid_date(date_string, format='%Y-%m-%d'):
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False

check_user_query = "SELECT id FROM users WHERE id = :user_id"
check_transaction_query = "SELECT user_id FROM transactions WHERE id = :transaction_id"
check_purchase_query = "SELECT transaction_id FROM purchases WHERE id = :purchase_id"

# gets purchases for a user (all or specific purchase)
@router.get("/", tags=["purchase"])
def get_purchases(user_id: int, transaction_id: int, purchase_id: int = -1, sort_by: str = "date", sort_order: str = "asc"):
    """ """
    ans = []

    # check if sort_by and sort_order is valid
    if sort_by not in ["date", "price", "category", "warranty_date", "return_date", "quantity"]:
        raise HTTPException(status_code=400, detail="Invalid sort_by")
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort_order")

    try: 
        with db.engine.begin() as connection:
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # check if transaction exists and belongs to user
            result = connection.execute(
                sqlalchemy.text(check_transaction_query),
                [{"transaction_id": transaction_id, "user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="Transaction not found")
            if result.user_id != user_id:
                raise HTTPException(status_code=400, detail="Transaction does not belong to user")

            if purchase_id == -1:
                # get all purchases for transaction
                ans = connection.execute(
                    sqlalchemy.text(
                        f"""
                        SELECT purchases.id, item, price, category, warranty_date, return_date, quantity
                        FROM purchases
                        JOIN transactions ON purchases.transaction_id = transactions.id
                        WHERE transaction_id = :transaction_id AND user_id = :user_id
                        ORDER BY {sort_by} {sort_order}
                        """
                    ), [{"transaction_id": transaction_id, "user_id": user_id}]).mappings().all()
            else:
                # check if purchase exists and belongs to transaction
                result = connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT transaction_id FROM purchases WHERE id = :purchase_id
                        """
                    ), [{"purchase_id": purchase_id}]).fetchone()
                if result is None:
                    raise HTTPException(status_code=404, detail="Purchase not found")
                if result.transaction_id != transaction_id:
                    raise HTTPException(status_code=400, detail="Purchase does not belong to transaction")

                # get specific purchase
                ans = connection.execute(
                    sqlalchemy.text(
                        f"""
                        SELECT purchases.id, item, price, category, warranty_date, return_date, quantity
                        FROM purchases
                        JOIN transactions ON purchases.transaction_id = transactions.id
                        WHERE transaction_id = :transaction_id AND user_id = :user_id AND purchases.id = :purchase_id
                        ORDER BY {sort_by} {sort_order}
                        """
                    ), [{"transaction_id": transaction_id, "purchase_id": purchase_id, "user_id": user_id}]).mappings().all()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    print(f"USER_{user_id}_TRANSACTION_{transaction_id}_PURCHASES: {ans}")

    # ex: [{"item": "TV", "price": 500.00, "category": "Electronics", "warranty_date": "2022-05-01", "return_date": "2021-06-01"}, ...]
    return ans



# creates a new purchase for a user
@router.post("/", tags=["purchase"])
def create_purchase(user_id: int, transaction_id: int, purchase: NewPurchase):
    """ """
    item = purchase.item
    price = float(purchase.price)
    quantity = purchase.quantity
    warranty_date = purchase.warranty_date
    return_date = purchase.return_date
    category = purchase.category

    # Validate inputs
    if not is_valid_date(warranty_date):
        raise HTTPException(status_code=400, detail="Invalid warranty date format")
    if not is_valid_date(return_date):
        raise HTTPException(status_code=400, detail="Invalid return date format")
    if not isinstance(price, int) or price <= 0:
        raise HTTPException(status_code=400, detail="Invalid price format")
    if not isinstance(quantity, int) or quantity <= 1:
        raise HTTPException(status_code=400, detail="Invalid quantity format")
    if category not in ['Groceries', 'Clothing and Accessories', 'Electronics', 'Home and Garden', 
                        'Health and Beauty', 'Entertainment', 'Travel', 'Automotive', 'Services', 
                        'Gifts and Special Occasions', 'Education', 'Fitness and Sports', 'Pets', 
                        'Office Supplies', 'Financial Services', 'Other']:
        raise HTTPException(status_code=400, detail="Invalid category")

    try:
        with db.engine.begin() as connection:
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # check if transaction exists and belongs to user
            result = connection.execute(
                sqlalchemy.text(check_transaction_query),
                [{"transaction_id": transaction_id, "user_id": user_id}]
            ).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="Transaction not found")
            if result.user_id != user_id:
                raise HTTPException(status_code=400, detail="Transaction does not belong to user")

            purchase_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO purchases (transaction_id, item, price, quantity, warranty_date, return_date, category)
                    VALUES (:transaction_id, :item, :price, :quantity, :warranty_date, :return_date, :category)
                    RETURNING id
                    """
                ), [{"transaction_id": transaction_id, "item": item, "price": price, "quantity": quantity, "warranty_date": warranty_date, "return_date": return_date, "category": category}]).scalar_one()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"purchase_id": purchase_id}



# deletes a specific purchase for a user
@router.delete("/{purchase_id}", tags=["purchase"])
def delete_purchase(user_id: int, transaction_id: int, purchase_id: int):
    """ """
    try:
        with db.engine.begin() as connection:
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # check if transaction exists and belongs to user
            result = connection.execute(
                sqlalchemy.text(check_transaction_query),
                [{"transaction_id": transaction_id, "user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="Transaction not found")
            if result.user_id != user_id:
                raise HTTPException(status_code=400, detail="Transaction does not belong to user")
            
            # check if purchase exists and belongs to transaction
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT transaction_id FROM purchases WHERE id = :purchase_id
                    """
                ), [{"purchase_id": purchase_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="Purchase not found")
            if result.transaction_id != transaction_id:
                raise HTTPException(status_code=400, detail="Purchase does not belong to transaction")

            # delete purchase
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM purchases
                    WHERE id = :purchase_id
                    """
                ), [{"purchase_id": purchase_id}])
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return "OK"

# updates a specific purchase for a user
@router.put("/{purchase_id}", tags=["purchase"])
def update_purchase(user_id: int, transaction_id: int, purchase_id: int, purchase: NewPurchase):
    """ """
    item = purchase.item
    price = purchase.price
    category = purchase.category
    warranty_date = purchase.warranty_date
    return_date = purchase.return_date
    quantity = purchase.quantity

    # Validate inputs
    if not is_valid_date(warranty_date):
        raise HTTPException(status_code=400, detail="Invalid warranty date format")
    if not is_valid_date(return_date):
        raise HTTPException(status_code=400, detail="Invalid return date format")
    if not isinstance(price, int) or price <= 0:
        raise HTTPException(status_code=400, detail="Invalid price format")
    if not isinstance(quantity, int) or quantity <= 1:
        raise HTTPException(status_code=400, detail="Invalid quantity format")
    if category not in ['Groceries', 'Clothing and Accessories', 'Electronics', 'Home and Garden', 
                        'Health and Beauty', 'Entertainment', 'Travel', 'Automotive', 'Services', 
                        'Gifts and Special Occasions', 'Education', 'Fitness and Sports', 'Pets', 
                        'Office Supplies', 'Financial Services', 'Other']:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    try:
        with db.engine.begin() as connection:
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # check if transaction exists and belongs to user
            result = connection.execute(
                sqlalchemy.text(check_transaction_query),
                [{"transaction_id": transaction_id, "user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="Transaction not found")
            if result.user_id != user_id:
                raise HTTPException(status_code=400, detail="Transaction does not belong to user")
            
            # check if purchase exists and belongs to transaction
            result = connection.execute(
                sqlalchemy.text(check_purchase_query), 
                [{"purchase_id": purchase_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="Purchase not found")
            if result.transaction_id != transaction_id:
                raise HTTPException(status_code=400, detail="Purchase does not belong to transaction")

            # update purchase
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE purchases
                    SET item = :item, price = :price, category = :category, warranty_date = :warranty_date, return_date = :return_date, quantity = :quantity
                    WHERE id = :purchase_id
                    """
                ), [{"purchase_id": purchase_id, "item": item, "price": price, "category": category, "warranty_date": warranty_date, "return_date": return_date, "quantity": quantity}])
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"item": item, "price": price, "category": category, "warranty_date": warranty_date, "return_date": return_date, "quantity": quantity}




# gets sum of money spent of different catagories of all purchases for a user
@router.get("/categories", tags=["purchase"])
def get_sum_per_category(user_id: int, transaction_id: int):
    """ """
    ans = []

    try: 
        with db.engine.begin() as connection:
            # ans stores query result as list of dictionaries/json
            ans = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT category, SUM(price) AS total
                    FROM purchases
                    WHERE transaction_id = :transaction_id
                    GROUP BY category
                    """
                ), [{"transaction_id": transaction_id}]).mappings().all()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    print(f"USER_{user_id}_TRANSACTION_{transaction_id}_PURCHASES_CATAGORIZED: {ans}")

    return ans