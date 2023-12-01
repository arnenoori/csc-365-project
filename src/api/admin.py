from fastapi import APIRouter, Depends
from src.api import auth

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