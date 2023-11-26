from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError
from datetime import datetime




# Gives user a financial recommendation based on their budgeting goals and spending habits
@router.get("/{user_id}/recommendation", tags=["chatbot"])
def get_financial_recommendation(user_id: int):
    """ """
    # GET user's budgeting goals

    # GET user's spending habits

    # GET user's info - income, expenses, etc.

    # Call's OpenAI's API to generate a financial recommendation

    return ""






