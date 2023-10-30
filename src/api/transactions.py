from fastapi import APIRouter
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError

router = APIRouter()

@router.get("/transaction/{user_id}", tags=["transaction"])
def get_transactions(user_id: int):
    result = None

    try: 
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT merchant, description, created_AT
                    FROM Transactions
                    where user_id = :user_id
                    """
                ), [{"user_id": user_id}])
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return result.fetchall()
