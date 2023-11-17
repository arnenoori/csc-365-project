from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import transactions, admin, auth, users, purchases, budget
import json
import logging
import sys
from starlette.middleware.cors import CORSMiddleware

description = """
Receipt App
"""

app = FastAPI(
    title="Receipt App",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Students",
        "email": "cpobrien@calpoly.edu",
    },
)

origins = ["https://potion-exchange.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(transactions.router)
app.include_router(users.router)
app.include_router(purchases.router)
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(budget.router)

@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response['message'].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)

@app.get("/")
async def root():
    return {"message": "Welcome to our Receipt App Backend."}
