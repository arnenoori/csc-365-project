from fastapi import APIRouter, HTTPException, UploadFile, File
import base64
import requests
import json
import os
from src.api.transactions import create_transaction
from src.api.purchases import create_purchase


router = APIRouter()
api_key = os.getenv('OPENAI_API_KEY')

@router.post("/", tags=["receipt"])
def upload_receipt(user_id: int, file: UploadFile = File(...)):
    try:
        # Encode the image to base64
        base64_image = base64.b64encode(file.file.read()).decode('utf-8')

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
                            "text": "What’s in this image?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
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

        # Extract the necessary data from the receipt_data
        store_name = receipt_data['store_name']
        items = receipt_data['items']  # This should be a list of items, where each item is a dictionary with 'item', 'price', and 'quantity' keys

        # Create a new transaction with the store name
        transaction_id = create_transaction(user_id, store_name)

        # Create a new purchase for each item in the receipt
        for item in items:
            create_purchase(user_id, transaction_id, item['item'], item['price'], item['quantity'])

        return {"message": "Receipt uploaded and processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))