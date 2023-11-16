from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError
from datetime import datetime

router = APIRouter(
    prefix="/user/{user_id}/transactions",
    tags=["transactions"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewTransaction(BaseModel):
    merchant: str
    description: str
    date: str

def is_valid_date(date_string, format='%Y-%m-%d'):
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False

check_transaction_query = "SELECT user_id FROM transactions WHERE id = :transaction_id"
check_user_query = "SELECT id FROM users WHERE id = :user_id"

# creates a new transaction for a user
@router.post("/", tags=["transactions"])
def create_transaction(user_id: int, transaction: NewTransaction):
    """ """
    merchant = transaction.merchant
    description = transaction.description
    date = transaction.date

    # check if date is valid
    if not is_valid_date(date):
        raise HTTPException(status_code=400, detail="Invalid date")

    try:
        with db.engine.begin() as connection:
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # add transaction to database
            transaction_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO transactions (user_id, merchant, description, date)
                    VALUES (:user_id, :merchant, :description)
                    RETURNING id
                    """
                ), [{"user_id": user_id, "merchant": merchant, "description": description, "date": date}]).scalar_one()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"transaction_id": transaction_id}

# gets transactions for a user (all or specific transaction)
@router.get("/", tags=["transactions"])
def get_transactions(user_id: int, transaction_id: int = -1, page: int = 1, page_size: int = 10):
    """ """
    offset = (page - 1) * page_size
    try: 
        with db.engine.begin() as connection:
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # get transactions
            if transaction_id == -1:
                ans = connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT id, merchant, description, date
                        FROM transactions
                        WHERE user_id = :user_id
                        ORDER BY created_at DESC
                        LIMIT :page_size OFFSET :offset
                        """
                    ), [{"user_id": user_id, "page_size": page_size, "offset": offset}]).mappings().all()
            else:
                ans = connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT id, merchant, description, date
                        FROM transactions
                        WHERE user_id = :user_id AND id = :transaction_id
                        ORDER BY created_at DESC
                        LIMIT :page_size OFFSET :offset
                        """
                    ), [{"user_id": user_id, "transaction_id": transaction_id, "page_size": page_size, "offset": offset}]).mappings().all()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    print(f"USER_{user_id}_TRANSACTIONS_PAGE_{page}: {ans}")

    return ans

# deletes a specific transaction for a user
@router.delete("/{transaction_id}", tags=["transactions"])
def delete_transaction(user_id: int, transaction_id: int):
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
            
            # delete transaction
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM transactions
                    WHERE id = :transaction_id AND user_id = :user_id
                    """
                ), [{"transaction_id": transaction_id, "user_id": user_id}])
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return "OK"

# updates a specific transaction for a user
@router.put("/{transaction_id}", tags=["transactions"])
def update_transaction(user_id: int, transaction_id: int, transaction: NewTransaction):
    """ """
    merchant = transaction.merchant
    description = transaction.description
    date = transaction.date

    # check if date is valid
    if not is_valid_date(date):
        raise HTTPException(status_code=400, detail="Invalid date")

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
            
            # update transaction
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE transactions
                    SET merchant = :merchant, description = :description, date = :date
                    WHERE id = :transaction_id AND user_id = :user_id
                    """
                ), [{"transaction_id": transaction_id, "user_id": user_id, "merchant": merchant, "description": description, "date": date}])
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"transaction_id": transaction_id, "merchant": merchant, "description": description}