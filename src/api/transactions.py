from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError
from datetime import datetime
import time

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
        year, month, day = date_string.split('-')
        if len(year) != 4 or len(month) != 2 or len(day) != 2:
            return False
        return True
    except ValueError:
        return False

check_transaction_query = "SELECT user_id FROM transactions WHERE id = :transaction_id"
check_user_query = "SELECT id FROM users WHERE id = :user_id"

# creates a new transaction for a user
@router.post("/", tags=["transactions"])
def create_transaction(user_id: int, transaction: NewTransaction):
    """ """
    start_time = time.time()

    merchant = transaction.merchant
    description = transaction.description
    date = transaction.date
    transaction_id = None

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
                    VALUES (:user_id, :merchant, :description, :date)
                    RETURNING id
                    """
                ), [{"user_id": user_id, "merchant": merchant, "description": description, "date": date}]).scalar_one()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
    
    end_time = time.time()
    print(f"time: {(end_time - start_time) * 1000}")

    return {"transaction_id": transaction_id}

# gets transactions for a user (all or specific transaction)
@router.get("/", tags=["transactions"])
def get_transactions(user_id: int, transaction_id: int = -1, page: int = 1, page_size: int = 10, sort_by: str = "date", sort_order: str = "asc", date_from: str = "1000-01-01", date_to: str = "9999-12-31", merchant: str = "%"):
    """ """
    start_time = time.time()
    
    # check if sort_by and sort_order is valid
    if sort_by not in ["date", "merchant"]:
        raise HTTPException(status_code=400, detail="Invalid sort_by")
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort_order")
    
    # check if date_from and date_to are valid
    if not is_valid_date(date_from):
        raise HTTPException(status_code=400, detail="Invalid date_from")
    if not is_valid_date(date_to):
        raise HTTPException(status_code=400, detail="Invalid date_to")
    
    offset = (page - 1) * page_size
    merchant = f"%{merchant}%"

    try: 
        with db.engine.begin() as connection:
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            if transaction_id == -1:
                # get all transactions for user
                ans = connection.execute(
                    sqlalchemy.text(
                        f"""
                        SELECT id, merchant, description, date
                        FROM transactions
                        WHERE user_id = :user_id AND (date BETWEEN :date_from AND :date_to) AND merchant ILIKE :merchant
                        ORDER BY {sort_by} {sort_order}
                        LIMIT :page_size OFFSET :offset
                        """
                    ), [{"user_id": user_id, "page_size": page_size, "offset": offset, "date_from": date_from, "date_to": date_to, "merchant": merchant}]).mappings().all()
            else:
                # check if transaction exists and belongs to user
                result = connection.execute(
                    sqlalchemy.text(check_transaction_query),
                    [{"transaction_id": transaction_id, "user_id": user_id}]).fetchone()
                if result is None:
                    raise HTTPException(status_code=404, detail="Transaction not found")
                if result.user_id != user_id:
                    raise HTTPException(status_code=400, detail="Transaction does not belong to user")
                
                # get specific transaction
                ans = connection.execute(
                    sqlalchemy.text(
                        f"""
                        SELECT id, merchant, description, date
                        FROM transactions
                        WHERE user_id = :user_id AND id = :transaction_id AND (date BETWEEN :date_from AND :date_to) AND merchant ILIKE :merchant
                        ORDER BY {sort_by} {sort_order}
                        LIMIT :page_size OFFSET :offset
                        """
                    ), [{"user_id": user_id, "transaction_id": transaction_id, "page_size": page_size, "offset": offset, "date_from": date_from, "date_to": date_to, "merchant": merchant}]).mappings().all()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    print(f"USER_{user_id}_TRANSACTIONS_PAGE_{page}: {ans}")
    end_time = time.time()
    print(f"time: {(end_time - start_time) * 1000}")

    # returns [{"id": id, "merchant": merchant, "description": description, "date": date}, ...]
    return ans

# deletes a specific transaction for a user
@router.delete("/{transaction_id}", tags=["transactions"])
def delete_transaction(user_id: int, transaction_id: int):
    """ """
    start_time = time.time()

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

    end_time = time.time()
    print(f"time: {(end_time - start_time) * 1000}")

    return "OK"

# updates a specific transaction for a user
@router.put("/{transaction_id}", tags=["transactions"])
def update_transaction(user_id: int, transaction_id: int, transaction: NewTransaction):
    """ """
    start_time = time.time()

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

    end_time = time.time()
    print(f"time: {(end_time - start_time) * 1000}")

    return {"transaction_id": transaction_id, "merchant": merchant, "description": description, "date": date}