from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewUser(BaseModel):
    name: str
    email: str

# creates a new user
@router.post("/", tags=["user"])
def create_user(new_user: NewUser):
    """ """
    name = new_user.name
    email = new_user.email
    user_id = None

    # Check if email already exists
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT id FROM users WHERE email = :email
                """
            ), [{"email": email}]).fetchone()
        if result is not None:
            raise HTTPException(status_code=409, detail="Email already in use")

    try:
        with db.engine.begin() as connection:
            user_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO users (name, email)
                    VALUES (:name, :email)
                    RETURNING id
                    """
                ), [{"name": name, "email": email}]).scalar_one()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"user_id": user_id}



# gets a user's name and email
@router.get("/{user_id}", tags=["user"])
def get_user(user_id: int):
    """ """
    try:
        with db.engine.begin() as connection:
            # ans stores query result as dictionary/json
            ans = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT name, email
                    FROM users
                    WHERE id = :user_id
                    """
                ), [{"user_id": user_id}]).mappings().all()[0]
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    if not ans: raise HTTPException(status_code=404, detail="User not found")

    print(f"USER_{user_id}: {ans}")

    # ex: {"name": "John Doe", "email": "jdoe@gmail"}
    return ans

# deletes a user
@router.delete("/{user_id}", tags=["user"])
def delete_user(user_id: int):
    """ """
    try:
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM users
                    WHERE id = :user_id
                    """
                ), [{"user_id": user_id}])
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return "OK"

# updates a user's name and email
@router.put("/{user_id}", tags=["user"])
def update_user(user_id: int, new_user: NewUser):
    """ """
    name = new_user.name
    email = new_user.email

    try:
        # Check if new email already exists
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT id FROM users WHERE email = :email
                    """
                ), [{"email": email}]).fetchone()
            
            if result is not None and result['id'] != user_id:
                raise HTTPException(status_code=409, detail="Email already in use")
        
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE users
                    SET name = :name, email = :email
                    WHERE id = :user_id
                    """
                ), [{"name": name, "email": email, "user_id": user_id}])
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"name": name, "email": email}