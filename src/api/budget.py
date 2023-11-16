from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError
from fastapi import HTTPException

router = APIRouter(
    prefix="/user/{user_id}/budgets",
    tags=["budgets"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewBudget(BaseModel):
    groceries: int
    clothing_and_accessories: int
    electronics: int
    home_and_garden: int
    health_and_beauty: int
    entertainment: int
    travel: int
    automotive: int
    services: int
    gifts_and_special_occasions: int
    education: int
    fitness_and_sports: int
    pets: int
    office_supplies: int
    financial_services: int
    other: int

check_budget_query = "SELECT user_id FROM budgets WHERE id = :budget_id"
check_user_query = "SELECT id FROM users WHERE id = :user_id"

# creates a new budget for a user
@router.post("/", tags=["budgets"])
def create_budget(user_id: int, budget: NewBudget):
    """ """
    budget_id = None

    # check if budget is valid
    for category in budget:
        if category is not None and category < 0:
            raise HTTPException(status_code=400, detail="Invalid budget")

    try:
        with db.engine.begin() as connection:
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")            

            # add budget to database
            budget_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO budgets (user_id, groceries, clothing_and_accessories, electronics, home_and_garden, health_and_beauty, entertainment, travel, automotive, services, gifts_and_special_occasions, education, fitness_and_sports, pets, office_supplies, financial_services, other)
                    VALUES (:user_id, :groceries, :clothing_and_accessories, :electronics, :home_and_garden, :health_and_beauty, :entertainment, :travel, :automotive, :services, :gifts_and_special_occasions, :education, :fitness_and_sports, :pets, :office_supplies, :financial_services, :other)
                    RETURNING id
                    """
                ), [{"user_id": user_id, 
                     "groceries": budget.groceries, 
                     "clothing_and_accessories": budget.clothing_and_accessories, 
                     "electronics": budget.electronics, 
                     "home_and_garden": budget.home_and_garden, 
                     "health_and_beauty": budget.health_and_beauty, 
                     "entertainment": budget.entertainment, 
                     "travel": budget.travel, 
                     "automotive": budget.automotive, 
                     "services": budget.services, 
                     "gifts_and_special_occasions": budget.gifts_and_special_occasions, 
                     "education": budget.education, 
                     "fitness_and_sports": budget.fitness_and_sports, 
                     "pets": budget.pets, 
                     "office_supplies": budget.office_supplies, 
                     "financial_services": budget.financial_services, 
                     "other": budget.other}]).scalar_one()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"budget_id": budget_id}

# gets a user's monthly budgets
@router.get("/", tags=["budgets"])
def get_budgets(user_id: int):
    """ """
    try:
        with db.engine.begin() as connection:
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # gets budgets from database
            ans = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT groceries, clothing_and_accessories, electronics, home_and_garden, health_and_beauty, entertainment, travel, automotive, services, gifts_and_special_occasions, education, fitness_and_sports, pets, office_supplies, financial_services, other
                    FROM budgets
                    WHERE user_id = :user_id
                    """
                ), [{"user_id": user_id}]).fetchone()
            if ans is None:
                raise HTTPException(status_code=404, detail="Budget not found")
    except DBAPIError as error:
        print(f"DBAPIError returned: <<<{error}>>>")

    return dict(ans)

# compare actual monthly spending to budget
@router.get("/compare", tags=["budgets"])
def compare_budgets_to_actual_spending(user_id: int):
    """ """
    try:
        with db.engine.begin() as connection:
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # gets budgets from database
            ans = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT groceries, clothing_and_accessories, electronics, home_and_garden, health_and_beauty, entertainment, travel, automotive, services, gifts_and_special_occasions, education, fitness_and_sports, pets, office_supplies, financial_services, other
                    FROM budgets
                    WHERE user_id = :user_id
                    """
                ), [{"user_id": user_id}]).fetchone()
            if ans is None:
                raise HTTPException(status_code=404, detail="Budget not found")

            # gets actual spending from database
            actual_spending = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT SUM(price) AS total
                    FROM purchases
                    JOIN transactions on purchases.transaction_id = transactions.id
                    WHERE user_id = :user_id
                    GROUP BY category
                    """
                ), [{"user_id": user_id}]).all()
    except DBAPIError as error:
        print(f"DBAPIError returned: <<<{error}>>>")

    # convert actual spending to dictionary
    actual_spending_dict = {}
    for row in actual_spending:
        actual_spending_dict[row[0]] = row[1]

    # compare actual spending to budget
    comparisons = {}
    for category in ans.keys():
        if ans[category] is not None:
            comparisons[category] = (actual_spending_dict[category], ans[category])
    
    return comparisons