from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError
from fastapi import HTTPException
from datetime import datetime, timedelta

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

def is_valid_date(date_string, format='%Y-%m-%d'):
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False

def is_first_day_of_month(date):
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    return date_obj.day == 1

def is_last_day_of_month(date):
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    return date_obj.day == (date_obj.replace(month=date_obj.month % 12 + 1, day=1) - timedelta(days=1)).day

check_budget_query = "SELECT user_id FROM budgets WHERE id = :budget_id"
check_user_query = "SELECT id FROM users WHERE id = :user_id"

# creates a new budget for a user
@router.post("/", tags=["budgets"])
def create_budget(user_id: int, budget: NewBudget):
    """ """
    budget_id = None

    # check if budget is valid
    for category, amt in vars(budget).items():
        print(f"category: {category}, amt: {amt}")
        if (amt is not None and (not isinstance(amt, int) or amt < 0)):
            raise HTTPException(status_code=400, detail="Invalid budget")
    
    try:
        with db.engine.begin() as connection:
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")

            # check if user already has a budget
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT id FROM budgets WHERE user_id = :user_id
                    """
                ), [{"user_id": user_id}]).fetchone()
            if result is not None:
                raise HTTPException(status_code=400, detail="User already has a budget")        

            # add budget to database
            budget_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO budgets (user_id, groceries, clothing_and_accessories, electronics, home_and_garden, 
                    health_and_beauty, entertainment, travel, automotive, services, gifts_and_special_occasions, education, 
                    fitness_and_sports, pets, office_supplies, financial_services, other)
                    VALUES (:user_id, :groceries, :clothing_and_accessories, :electronics, :home_and_garden, :health_and_beauty, 
                    :entertainment, :travel, :automotive, :services, :gifts_and_special_occasions, :education, :fitness_and_sports, 
                    :pets, :office_supplies, :financial_services, :other)
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
                    SELECT groceries, clothing_and_accessories, electronics, home_and_garden, health_and_beauty, entertainment, travel, 
                    automotive, services, gifts_and_special_occasions, education, fitness_and_sports, pets, office_supplies, 
                    financial_services, other
                    FROM budgets
                    WHERE user_id = :user_id
                    """
                ), [{"user_id": user_id}]).fetchone()
            if ans is None:
                raise HTTPException(status_code=404, detail="Budget not found")
    except DBAPIError as error:
        print(f"DBAPIError returned: <<<{error}>>>")

    return dict(ans._mapping)

# updates a user's monthly budgets
@router.put("/{budget_id}", tags=["budgets"])
def update_budget(user_id: int, budget_id: int, budget: NewBudget):
    """ """
    # check if budget is valid
    for category, amt in vars(budget).items():
        print(f"category: {category}, amt: {amt}")
        if amt is None or not isinstance(amt, int) or amt < 0:
            raise HTTPException(status_code=400, detail="Invalid budget")
    try:
        with db.engine.begin() as connection:
            # check if budget exists
            result = connection.execute(
                sqlalchemy.text(check_budget_query), 
                [{"budget_id": budget_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="Budget not found")
            
            # update budget in database
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE budgets
                    SET groceries = :groceries, clothing_and_accessories = :clothing_and_accessories, electronics = :electronics, 
                    home_and_garden = :home_and_garden, health_and_beauty = :health_and_beauty, entertainment = :entertainment, 
                    travel = :travel, automotive = :automotive, services = :services, gifts_and_special_occasions = :gifts_and_special_occasions, 
                    education = :education, fitness_and_sports = :fitness_and_sports, pets = :pets, office_supplies = :office_supplies, 
                    financial_services = :financial_services, other = :other
                    WHERE id = :budget_id
                    """
                ), [{"budget_id": budget_id, 
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
                     "other": budget.other}])
    except DBAPIError as error:
        print(f"DBAPIError returned: <<{error}>>>")
    
    return {"budget_id": budget_id, "groceries": budget.groceries, "clothing_and_accessories": budget.clothing_and_accessories, 
            "electronics": budget.electronics, "home_and_garden": budget.home_and_garden, "health_and_beauty": budget.health_and_beauty, 
            "entertainment": budget.entertainment, "travel": budget.travel, "automotive": budget.automotive, "services": budget.services, 
            "gifts_and_special_occasions": budget.gifts_and_special_occasions, "education": budget.education, 
            "fitness_and_sports": budget.fitness_and_sports, "pets": budget.pets, "office_supplies": budget.office_supplies, 
            "financial_services": budget.financial_services, "other": budget.other}

# compare actual monthly spending to budget
@router.get("/compare", tags=["budgets"])
def compare_budgets_to_actual_spending(user_id: int, date_from: str = None, date_to: str = None):
    """ """
    try:
        with db.engine.begin() as connection:
            # check if date_from and date_to are valid
            if date_from is not None and not is_valid_date(date_from) :
                raise HTTPException(status_code=400, detail="Invalid date_from")
            if date_to is not None and not is_valid_date(date_to):
                raise HTTPException(status_code=400, detail="Invalid date_to")
            
            # set date_from to first day of current month and date_to to current day if not specified
            now = datetime.now()
            if date_from is None:
                date_from = datetime(now.year, now.month, 1).strftime('%Y-%m-%d')
            elif not is_first_day_of_month(date_from):
                raise HTTPException(status_code=400, detail="date_from must be first day of month")
            if date_to is None:
                # current day is fine b/c there shouldn't be any purchases in the future
                date_to = datetime(now.year, now.month, now.day).strftime('%Y-%m-%d')
            elif not is_last_day_of_month(date_to):
                raise HTTPException(status_code=400, detail="date_to must be last day of month")
            
            print(f"date_from: {date_from}, date_to: {date_to}")
            
            # check if user exists
            result = connection.execute(
                sqlalchemy.text(check_user_query), 
                [{"user_id": user_id}]).fetchone()
            if result is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # gets budgets from database
            budgets = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT groceries, clothing_and_accessories, electronics, home_and_garden, health_and_beauty, entertainment, 
                    travel, automotive, services, gifts_and_special_occasions, education, fitness_and_sports, pets, office_supplies, 
                    financial_services, other
                    FROM budgets
                    WHERE user_id = :user_id
                    """
                ), [{"user_id": user_id}]).fetchone()
            if budgets is None:
                raise HTTPException(status_code=404, detail="Budget not found")

            # gets actual spending from database
            actual_spending = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT category, SUM(price) AS total
                    FROM purchases
                    JOIN transactions on purchases.transaction_id = transactions.id
                    WHERE user_id = :user_id AND (date BETWEEN :date_from AND :date_to)
                    GROUP BY category
                    """
                ), [{"user_id": user_id, "date_from": date_from, "date_to": date_to}]).all()
    except DBAPIError as error:
        print(f"DBAPIError returned: <<<{error}>>>")

    # convert actual spending to dictionary
    actual_spending_dict = {}
    for row in actual_spending:
        if row.category is not None:
            actual_spending_dict[row.category.lower().replace(" ", "_")] = row.total
        else:
            actual_spending_dict['other'] = row.total

    print(f"actual_spending_dict: {actual_spending_dict}")

    # compare actual spending to budget
    comparisons = {}
    for category,amount in dict(budgets._mapping).items():
        if category in actual_spending_dict:
            comparisons[category] = (actual_spending_dict[category], budgets[category])
        else:
            comparisons[category] = (0, budgets[category])
    
    # in form of {category: (actual spending, budget), ...}
    return comparisons

# gets sum of money spent of different catagories of all purchases for a user
@router.get("/categories", tags=["budgets"])
def get_all_purchases_categorized(user_id: int):
    """ """
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

    return ans