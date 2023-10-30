from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import random
import string

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/info/")
def get_shop_info():
    return {
        "Project Name": "Receipt App",
        "Contributors": ["Connor OBrien", "Arne Noori", "Bryan Nguyen", "Sebastian Thau"]
    }