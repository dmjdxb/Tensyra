# whoop_api.py
import requests
import os

WHOOP_AUTH_URL = "https://api.whoop.com/oauth/oauth2/token"
WHOOP_DATA_URL = "https://api.whoop.com/users/activity"

def get_whoop_token(code: str):
    data = {
        'grant_type': 'authorization_code',
        'client_id': os.getenv("WHOOP_CLIENT_ID"),
        'client_secret': os.getenv("WHOOP_CLIENT_SECRET"),
        'code': code,
        'redirect_uri': "https://yourapp.streamlit.app"
    }
    response = requests.post(WHOOP_AUTH_URL, data=data)
    return response.json()

def get_whoop_data(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    r = requests.get("https://api.whoop.com/v1/recovery", headers=headers)
    return r.json()
