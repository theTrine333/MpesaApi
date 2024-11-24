from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import base64

# Load environment variables
load_dotenv()

# Daraja API credentials
CONSUMER_KEY = os.getenv("DARAJA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("DARAJA_CONSUMER_SECRET")
BASE_URL = os.getenv("DARAJA_BASE_URL")

app = FastAPI()

# Function to get the access token
def get_access_token():
    url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url,  headers = { 'Authorization': 'Basic WXdXMkdCTzBGMUxGcFkxam1TYjhjRGpnd0VNUGFLa0FNYk12S0Zzc0VLcTdUVENZOjVDQzBkZHlMQTN3WWV4UEpGcHQ3NDV6cUFVcVpRbG5XQmZBNlliOHJRamRrZThkM044WDRuM2hGbm5wMm4zdGI=' })
    if response.status_code == 200:
        return response.json()["access_token"]
    raise HTTPException(status_code=500, detail="Failed to get access token")


@app.post("/stk_push/")
def stk_push(phone_number: str, amount: int):
    """STK Push endpoint."""
    token = get_access_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    business_short_code = "174379"  # Replace with your shortcode
    passkey = "your_passkey_here"  # Replace with your Lipa na M-Pesa passkey
    password = base64.b64encode(f"{business_short_code}{passkey}{timestamp}".encode()).decode()

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://127.0.0.1/callback",  # Replace with your actual callback URL
        "AccountReference": "Test",
        "TransactionDesc": "Payment"
    }

    url = f"{BASE_URL}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail=response.text)

@app.get("/callback")
def handle_failed():
    return {
        "status_code":505,
        "message":"Couldn't process data at the moment"
    }

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Daraja FastAPI integration!",
        "access_token":get_access_token()
    }
