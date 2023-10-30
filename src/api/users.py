from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError
from enum import Enum

router = APIRouter(
    prefix="/users/{user_id}",
    tags=["user"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewUser(BaseModel):
    name: str
    email: str
    password: str

@router.post("/")
def create_cart(new_user: NewUser):
    """ """
    name = new_user.name
    email = new_user.email
    password = new_user.password

    try:
        with db.engine.begin() as connection:
            user_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO users (name, email)
                    VALUES (:name, :email)
                    RETURNING id
                    """
                ), [{"name": name, "email": email}]).scalar_one().id
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"user_id": user_id}
