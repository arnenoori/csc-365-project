from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError

router = APIRouter(
    prefix="/user/{user_id}/transactions",
    tags=["transaction"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewTransaction(BaseModel):
    merchant: str
    description: str

# gets all transactions for a user
@router.get("/", tags=["transaction"])
def get_transactions(user_id: int):
    """ """
    ans = []

    try: 
        with db.engine.begin() as connection:
            # ans stores query result as list of dictionaries/json
            ans = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT merchant, description, created_at
                    FROM transactions
                    where user_id = :user_id
                    """
                ), [{"user_id": user_id}]).mappings().all()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    print(f"USER_{user_id}_TRANSACTIONS: {ans}")

    # ex: [{"merchant": "Walmart", "description": "got groceries", "created_at": "2021-05-01 12:00:00"}, ...]
    return ans

# creates a new transaction for a user
@router.post("/", tags=["transaction"])
def create_transaction(user_id: int, transaction: NewTransaction):
    """ """
    merchant = transaction.merchant
    description = transaction.description

    try: 
        with db.engine.begin() as connection:
            transaction_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO transactions (user_id, merchant, description)
                    VALUES (:user_id, :merchant, :description)
                    RETURNING id
                    """
                ), [{"user_id": user_id, "merchant": merchant, "description": description}]).scalar_one()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"transaction_id": transaction_id}




# gets a specific transaction for a user
@router.get("/{transaction_id}", tags=["transaction"])
def get_transaction(user_id: int, transaction_id: int):
    """ """
    try: 
        with db.engine.begin() as connection:
            # ans stores query result as dictionary/json
            ans = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT merchant, description, created_at
                    FROM transactions
                    WHERE id = :transaction_id
                    """
                ), [{"transaction_id": transaction_id}]).scalar_one().to_dict()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    print(f"USER_{user_id}_TRANSACTION_{transaction_id}: {ans}")

    # ex: {"merchant": "Walmart", "description": "got groceries", "created_at": "2021-05-01 12:00:00"}
    return ans

# deletes a specific transaction for a user
@router.delete("/{transaction_id}", tags=["transaction"])
def delete_transaction(user_id: int, transaction_id: int):
    """ """
    try:
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM transactions
                    WHERE id = :transaction_id
                    """
                ), [{"transaction_id": transaction_id}])
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return "OK"

# updates a specific transaction for a user
@router.put("/{transaction_id}", tags=["transaction"])
def update_transaction(user_id: int, transaction_id: int, transaction: NewTransaction):
    """ """
    merchant = transaction.merchant
    description = transaction.description

    try: 
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE transactions
                    SET merchant = :merchant, description = :description
                    WHERE id = :transaction_id
                    """
                ), [{"transaction_id": transaction_id, "merchant": merchant, "description": description}])
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"merchant": merchant, "description": description}