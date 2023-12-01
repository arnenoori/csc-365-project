from fastapi import APIRouter, HTTPException, Depends
import openai
from src.api import auth
from src import database as db
import sqlalchemy
import logging

router = APIRouter(
    prefix="/user/{user_id}/query",
    tags=["query"],
    dependencies=[Depends(auth.get_api_key)],
)

openai.api_key = 'your-api-key'

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "You are a helpful assistant."},
    ]
)

print(response['choices'][0]['message']['content'])

def parse_query(user_query: str):
    """
    This function takes a user's natural language query and converts it into an SQL query.
    Currently, it only supports queries for total spending at a specific store.
    You can extend this function to support more types of queries.
    """
    # This is a very basic implementation of the parsing function
    # In a real-world application, you would use a more sophisticated approach
    # like natural language processing (NLP) to understand the user's query
    store_name = user_query.split(" ")[-1]
    return sqlalchemy.text(
        """
        SELECT SUM(price) AS total_spent
        FROM transactions
        WHERE store = :store_name
        """
    ), {"store_name": store_name}

@router.get("/{user_query}", tags=["query"])
def get_query(user_id: int, user_query: str):
    try:
        # Parse the user's query into an SQL query
        sql_query, params = parse_query(user_query)

        # Execute the SQL query and fetch the result
        with db.engine.begin() as connection:
            result = connection.execute(sql_query, **params).fetchone()

        # If the query returned no result, raise an HTTPException with a 404 status code
        if result is None:
            raise HTTPException(status_code=404, detail="No result found for your query.")

        return {"total_spent": result["total_spent"]}

    except Exception as e:
        # Log the exception for debugging
        logging.error(f"An error occurred while processing the query: {e}")

        # Raise an HTTPException with a 500 status code
        raise HTTPException(status_code=500, detail=str(e))