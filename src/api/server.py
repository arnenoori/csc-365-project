from fastapi import FastAPI, HTTPException, exceptions, File, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import transactions, admin, users, purchases, budget
from src import database as db
import sqlalchemy
from sqlalchemy.exc import DBAPIError
import json
import logging
import boto3
import requests
import os
import time
from starlette.middleware.cors import CORSMiddleware
from src.api.transactions import create_transaction
from src.api.purchases import create_purchase
from src.api.transactions import NewTransaction
from src.api.purchases import NewPurchase

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
        "email": "agnoori@calpoly.edu",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

s3 = boto3.resource(
    's3',
    aws_access_key_id= os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

api_key = os.getenv('OPENAI_API_KEY')

bucket = s3.Bucket('user-receipts-upload')

KB = 1024
MB = 1024 * KB

SUPPORTED_FILES = {
    'image/png': 'png',
    'image/jpeg': 'jpeg',
    'application/pdf': 'pdf'
}

#had issues with magic so using this to check file type
def get_file_type(contents):
    # Common file headers (first few bytes)
    file_signatures = {
        b'\xFF\xD8\xFF\xDB': 'image/jpeg',
        b'\xFF\xD8\xFF\xE0': 'image/jpeg',
        b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A': 'image/png',
        b'\x25\x50\x44\x46\x2D': 'application/pdf'
    }

    # Check the first few bytes against common signatures
    for signature, file_type in file_signatures.items():
        if contents.startswith(signature):
            return file_type

    return 'unknown'


@app.post("/upload_receipt")
async def upload_receipt_to_S3(user_id: int, file: UploadFile = File(...)):
    if not file:
        raise HTTPException (
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File not found'

        )
    
    contents = await file.read()
    file_size = len(contents)

    #setting file size limit to 10MB
    if not 0 < file_size <= 10 * MB:
        raise HTTPException (
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File size must be between 0 and 10 MB'

        )
    
    file_type = get_file_type(contents)
    if file_type not in SUPPORTED_FILES:
        raise HTTPException (
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='file type: {file_type} not supported'
        )
    
    #used as unique identifier
    upload_time = time.time()
    
    await s3_upload(contents=contents, key=f'{file.filename}.{int(upload_time)}.{SUPPORTED_FILES[file_type]}')
    print("upload successful")
    
    image_url = f"https://{os.getenv('AWS_S3_BUCKET_NAME')}.s3.us-west-1.amazonaws.com/{file.filename}.{int(upload_time)}.{SUPPORTED_FILES[file_type]}"

    #once this returns, all receipt info will be in purchases and transactions table assuming openai func works with proper formatting
    transaction_id = await openai_process_receipt(user_id=user_id, img_url=image_url, file=file)

    print("openai processing done")

    #Storing receipt_url in database, linking it to user with transaction_id, receipt data done in func call right above
    try: 
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO receipts (transaction_id, url, parsed_data)
                    VALUES (:transaction_id, :url, :parsed_data)
                    """
                ), {"transaction_id": transaction_id['transaction_id'], "url": image_url, "parsed_data": ""})
            print("receipt_url inserted into receipts table")
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return {"image_url": image_url}



async def s3_upload(contents: bytes, key: str):
    print("attempting to upload image to s3")
    bucket.put_object(Key=key, Body=contents)


#openai api parses receipt and inserts purchases and transcation info into tables,
#returns transaction id so receipt image and all of its info can be linked by that
async def openai_process_receipt(user_id: int, img_url: str, file: UploadFile = File(...)):
    try:

        # Prepare the headers and payload for the OpenAI API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """return the information in this receipt as neatly formatted JSON. Only return store name, date, all items and their associated price and quantity. only provide a compliant JSON response following this format without deviation:
                                        {
                                          "store_name": "store name",
                                          "date": "the date",
                                          "items": [
                                            {
                                              "name": "item name",
                                              "price": 0.99,
                                              "quantity": 5
                                            }
                                          ]
                                        } """
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"{img_url}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # Parse the response to extract the receipt data
        receipt_data = json.loads(response.text)
        
        # Extract the content string
        content = receipt_data['choices'][0]['message']['content']

        # Remove the triple backticks and any additional text around the JSON
        
        json_str = content.split('```json\n', 1)[1]
        json_str = json_str.rsplit('\n```', 1)[0]

        # Parse the JSON string
        receipt_json = json.loads(json_str)

        # Now receipt_json contains the raw JSON data
        print("\n {0} \n".format(receipt_json))
    
        # Extract the necessary data from the receipt_data
        store_name = receipt_json['store_name']
        receipt_date = receipt_json['date']
        
        items = receipt_json['items']  # This should be a list of items, where each item is a dictionary with 'item', 'price', and 'quantity' keys
        
        # Create a new transaction with the store name
        created_transaction = NewTransaction(merchant=store_name, description="", date=receipt_date)

        transaction_id = create_transaction(user_id, created_transaction)
        print("created transaction {0}".format(transaction_id))
        
        # Create a new purchase for each item in the receipt
        for item in items:
            created_purchase = NewPurchase(item=item['name'], price=item['price'], quantity=item['quantity'], category="", warranty_date="2023-11-16", return_date="2023-11-16")
            create_purchase(user_id, transaction_id['transaction_id'], created_purchase)

        return transaction_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    
#gets all of a user's receipt image url's from database using user_id - working
@app.get("/user/{user_id}/receipts")
async def get_receipts(user_id: int):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT r.url
                    FROM receipts AS r
                    JOIN transactions AS t ON r.transaction_id = t.id
                    WHERE t.user_id = :user_id
                    """
                ), {"user_id": user_id}
            )
            receipt_urls = [row[0] for row in result]
            return {"receipts": receipt_urls}
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
        raise HTTPException(status_code=500, detail=str(error))


app.include_router(transactions.router)
app.include_router(users.router)
app.include_router(purchases.router)
app.include_router(admin.router)
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

