from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError

router = APIRouter(
    prefix="/user/{user_id}/purchases",
    tags=["purchase"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewPurchase(BaseModel):
    item: str
    price: float
    category: str
    warranty_date: str
    return_date: str

@router.get("/", tags=["purchase"])
def get_purchases(user_id: int, transaction_id: int):
    """ """
    ans = []

    try: 
        with db.engine.begin() as connection:
            # ans stores query result as list of dictionaries/json
            ans = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT item, price, category, warranty_date, return_date
                    FROM purchases
                    WHERE transaction_id = :transaction_id
                    """
                ), [{"transaction_id": transaction_id}]).mappings().all()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    print(f"USER_{user_id}_TRANSACTION_{transaction_id}_PURCHASES: {ans}")

    # ex: [{"item": "TV", "price": 500.00, "category": "Electronics", "warranty_date": "2022-05-01", "return_date": "2021-06-01"}, ...]
    return ans


@router.post("/", tags=["purchase"])
def create_purchase(user_id: int, transaction_id: int, purchase: NewPurchase):
    """ """
    item = purchase.item
    price = purchase.price
    category = purchase.category
    warranty_date = purchase.warranty_date
    return_date = purchase.return_date

    try: 
        with db.engine.begin() as connection:
            purchase_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO purchases (transaction_id, item, price, category, warranty_date, return_date)
                    VALUES (:transaction_id, :item, :price, :category, :warranty_date, :return_date)
                    RETURNING id
                    """
                ), [{"transaction_id": transaction_id, "item": item, "price": price, "category": category, "warranty_date": warranty_date, "return_date": return_date}]).scalar_one()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"purchase_id": purchase_id}