# auth.py
import firebase_admin
from firebase_admin import auth, credentials
import streamlit as st
import json

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)

def sign_up(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return user.uid
    except Exception as e:
        st.error(f"Signup error: {str(e)}")
        return None

def sign_in(email, password):
    # Firebase Admin SDK doesn't support password verification
    st.warning("Admin SDK cannot verify passwords. For production, use a custom backend or identity provider.")
    return email  # Simulate user ID as email
