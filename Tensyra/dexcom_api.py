# dexcom_api.py
import os
import requests

DEXCOM_AUTH_URL = "https://sandbox-api.dexcom.com/v2/oauth2/token"

def get_dexcom_auth_link():
    client_id = os.getenv("DEXCOM_CLIENT_ID")
    redirect_uri = os.getenv("DEXCOM_REDIRECT_URI")
    return (
        f"https://sandbox-api.dexcom.com/v2/oauth2/login?"
        f"client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=offline_access"
    )

def exchange_dexcom_code_for_token(code):
    data = {
        "client_id": os.getenv("DEXCOM_CLIENT_ID"),
        "client_secret": os.getenv("DEXCOM_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": os.getenv("DEXCOM_REDIRECT_URI")
    }
    r = requests.post(DEXCOM_AUTH_URL, data=data)
    return r.json()

def get_glucose_data(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    url = "https://sandbox-api.dexcom.com/v2/users/self/egvs?startDate=2023-12-01T00:00:00&endDate=2023-12-01T23:59:00"
    r = requests.get(url, headers=headers)
    return r.json()
