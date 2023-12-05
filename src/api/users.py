from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError
import re
from datetime import datetime, timedelta
import time

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewUser(BaseModel):
    name: str
    email: str

def is_valid_email(email):
    email_regex = r'^[A-Za-z0-9._+%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'
    return bool(re.match(email_regex, email))

def is_valid_name(name):
    name_regex = r'^[A-Za-z\'\-_]+$'
    return bool(re.match(name_regex, name))

check_user_query = "SELECT id FROM users WHERE id = :user_id"


# creates a new user
@router.post("/", tags=["user"])
def create_user(new_user: NewUser):
    """ """
    start_time = time.time()
    name = new_user.name
    email = new_user.email
    user_id = None

    # check if name is valid
    if not is_valid_name(name):
        raise HTTPException(status_code=400, detail="Invalid name")

    # check if email is valid
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email")

    try:
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

        # add user to database
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
        print(f"DBAPIError returned: <<<{error}>>>")
    except Exception as error:
        print(f"Internal Server Error returned: <<<{error}>>>")

    end_time = time.time()
    print(f"time: {(end_time - start_time) * 1000}")

    return {"user_id": user_id}



# gets a user's name and email
@router.get("/{user_id}", tags=["user"])
def get_user(user_id: int):
    """ """
    start_time = time.time()
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
                ), [{"user_id": user_id}]).fetchone()
            if ans is None:
                raise HTTPException(status_code=404, detail="User not found")
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    print(f"USER_{user_id}: {ans.name}, {ans.email}")
    end_time = time.time()
    print(f"time: {(end_time - start_time) * 1000}")

    # ex: {"name": "John Doe", "email": "jdoe@gmail"}
    return {"name": ans.name, "email": ans.email}

# deletes a user
@router.delete("/{user_id}", tags=["user"])
def delete_user(user_id: int):
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
            
            # delete user
            connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM users
                    WHERE id = :user_id
                    """
                ), [{"user_id": user_id}])
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
    end_time = time.time()
    print(f"time: {(end_time - start_time) * 1000}")

    return "OK"

# updates a user's name and email
@router.put("/{user_id}", tags=["user"])
def update_user(user_id: int, new_user: NewUser):
    """ """
    start_time = time.time()
    name = new_user.name
    email = new_user.email

    # check if name is valid
    if not is_valid_name(name):
        raise HTTPException(status_code=400, detail="Invalid name")

    # check if email is valid
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Invalid email")

    try:
        with db.engine.begin() as connection:
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # check if new email already exists
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT id FROM users WHERE email = :email
                    """
                ), [{"email": email}]).fetchone()
            if result is not None and result.id != user_id:
                raise HTTPException(status_code=409, detail="Email already in use")

            # update user
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
    end_time = time.time()
    print(f"time: {(end_time - start_time) * 1000}")

    return {"name": name, "email": email}

# gets sum of money spent of different catagories of all purchases for a user
@router.get("/{user_id}/categories", tags=["user"])
def get_all_purchases_categorized(user_id: int):
    """ """
    start_time = time.time()
    ans = []

    try: 
        with db.engine.begin() as connection:
            # ans stores query result as list of dictionaries/json
            ans = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT category, SUM(price) AS total
                    FROM purchases AS p
                    JOIN transactions AS t ON p.transaction_id = t.id
                    WHERE t.user_id = :user_id
                    GROUP BY category
                    ORDER BY total
                    """
                ), [{"user_id": user_id}]).mappings().all()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    print(f"USER_{user_id}_PURCHASES_CATAGORIZED: {ans}")
    end_time = time.time()
    print(f"time: {(end_time - start_time) * 1000}")

    return ans

# Get warranty of all purchases for a user 
# and return purchases that are going to expire within a week
@router.get("/{user_id}/warranty", tags=["user"])
def get_all_purchases_warranty(user_id: int):
    start_time = time.time()
    ans = []

    try:
        with db.engine.begin() as connection:
            # Calculate the date one week from now
            one_week_from_now = datetime.now() + timedelta(weeks=1)

            # ans stores query result as a list of dictionaries/json
            ans = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT item
                    FROM purchases AS p
                    JOIN transactions AS t ON p.transaction_id = t.id
                    WHERE t.user_id = :user_id
                    AND p.warranty_date::timestamp <= :one_week_from_now
                    ORDER BY p.warranty_date
                    """
                ), {"user_id": user_id, "one_week_from_now": one_week_from_now}
            ).mappings().all()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    print(f"USER_{user_id}_PURCHASES_WARRANTY: {ans}")
    end_time = time.time()
    print(f"time: {(end_time - start_time) * 1000}")

    return ans

# get public.user from auth.user
@router.get("/auth/{auth_id}", tags=["user"])
def get_auth_user(auth_id: int):
    """ """
    try:
        with db.engine.begin() as connection:
            ans = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT id, name, email
                    FROM users
                    WHERE auth_id = :auth_id
                    """
                ), [{"auth_id": auth_id}]).fetchone()
            if ans is None:
                raise HTTPException(status_code=404, detail="User not found")
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"id": ans.id, "name": ans.name, "email": ans.email}