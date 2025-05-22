# main.py
import streamlit as st
import pandas as pd
from logic import calculate_macros, analyze_glucose, calculate_mas_score
from meal_ai import generate_meal_plan
from whoop_api import get_whoop_auth_link, exchange_whoop_code_for_token, get_whoop_recovery
import streamlit as st
import urllib.parse
from dexcom_api import get_dexcom_auth_link, exchange_dexcom_code_for_token, get_glucose_data
from auth import init_firebase, sign_up, sign_in


#======Log in ==========
# Initialize Firebase
init_firebase()

# Session state for login
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.title("Welcome to NutriAI")
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Sign In"):
            user = sign_in(email, password)
            if user:
                st.session_state.user = user
                st.experimental_rerun()

    with tab2:
        new_email = st.text_input("New Email")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            user = sign_up(new_email, new_password)
            if user:
                st.session_state.user = user
                st.experimental_rerun()
else:
    st.sidebar.success(f"Logged in as {st.session_state.user}")

#=======Main=============
st.set_page_config(page_title="NutriAI", layout="wide")

st.title("🥗 NutriAI: Adaptive Meal Intelligence")

st.sidebar.header("User Profile")

# Basic inputs
weight = st.sidebar.number_input("Weight (kg)", min_value=40.0, max_value=150.0, value=75.0)
goal = st.sidebar.selectbox("Goal", ["cut", "maintain", "gain"])
diet = st.sidebar.selectbox("Dietary Preference", ["gluten-free", "FODMAP", "low sugar", "keto", "carnivore", "vegan", "vegetarian"])

# Simulated glucose + WHOOP data
st.sidebar.subheader("Simulated Data Input (for testing)")

glucose_raw = st.sidebar.text_area("Glucose readings (e.g. 92, 110, 140, 135)", "90, 100, 105, 110, 120")
glucose_values = list(map(int, glucose_raw.strip().split(",")))

recovery_score = st.sidebar.slider("WHOOP Recovery Score", 0, 100, 70)
hrv_score = st.sidebar.slider("HRV Score", 0, 100, 60)
sleep_score = st.sidebar.slider("Sleep Score", 0, 100, 75)
macro_adherence = st.sidebar.slider("Macro Adherence", 0, 100, 80)
symptoms_score = st.sidebar.slider("Symptoms Score", 0, 100, 85)

if st.sidebar.button("Generate Plan"):
    # Analyze glucose data
    glucose_stability, flags = analyze_glucose(glucose_values)

    # Calculate macros
    macros = calculate_macros(weight, goal, recovery_score, glucose_stability)

    # Calculate MAS Score
    mas = calculate_mas_score(glucose_stability, recovery_score, hrv_score, sleep_score, macro_adherence, symptoms_score)

    # Display dashboard
    st.subheader("Metabolic Snapshot")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("MAS Score", mas)
        st.metric("Recovery Score", recovery_score)
        st.metric("Glucose Stability", glucose_stability)

    with col2:
        st.metric("Protein (g)", macros['protein'])
        st.metric("Carbs (g)", macros['carbs'])
        st.metric("Fat (g)", macros['fat'])

    if flags:
        st.warning("⚠️ Glucose Flags: " + ", ".join(flags))

    st.subheader("AI-Generated Meal Plan")
    meal_plan = generate_meal_plan(macros, diet)
    st.markdown(meal_plan)

else:
    st.info("Fill out your profile and click **Generate Plan** to start.")


# WHOOP integration=====================
st.sidebar.subheader("WHOOP Integration")
whoop_code = st.query_params.get("code")

if whoop_code:
    tokens = exchange_whoop_code_for_token(whoop_code)
    access_token = tokens.get("access_token")

    if access_token:
        recovery_data = get_whoop_recovery(access_token)
        st.sidebar.success("WHOOP Connected")
        recovery_score = recovery_data['recovery'][0]['score']
    else:
        st.sidebar.error("WHOOP token exchange failed")
else:
    whoop_link = get_whoop_auth_link()
    st.sidebar.markdown(f"[Connect WHOOP]({whoop_link})")

# Use recovery_score in downstream logic=====================

# whoop_api.py============
import os
import requests

WHOOP_AUTH_URL = "https://api.whoop.com/oauth/oauth2/token"

def get_whoop_auth_link():
    client_id = os.getenv("WHOOP_CLIENT_ID")
    redirect_uri = os.getenv("WHOOP_REDIRECT_URI")
    return f"https://api.whoop.com/oauth/oauth2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope=read:recovery read:profile"

def exchange_whoop_code_for_token(code):
    response = requests.post(WHOOP_AUTH_URL, data={
        "grant_type": "authorization_code",
        "code": code,
        "client_id": os.getenv("WHOOP_CLIENT_ID"),
        "client_secret": os.getenv("WHOOP_CLIENT_SECRET"),
        "redirect_uri": os.getenv("WHOOP_REDIRECT_URI")
    })
    return response.json()

def get_whoop_recovery(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get("https://api.whoop.com/v1/recovery", headers=headers)
    return r.json()




# Dexcom integration=====================
st.sidebar.subheader("Dexcom Integration")
dexcom_code = st.query_params.get("dexcom_code_returned")

if dexcom_code:
    dexcom_tokens = exchange_dexcom_code_for_token(dexcom_code)
    dexcom_access_token = dexcom_tokens.get("access_token")

    if dexcom_access_token:
        glucose_payload = get_glucose_data(dexcom_access_token)
        glucose_values = [point['value'] for point in glucose_payload['egvs']]
        st.sidebar.success("Dexcom Connected")
    else:
        st.sidebar.error("Dexcom token exchange failed")
else:
    dexcom_link = get_dexcom_auth_link()
    st.sidebar.markdown(f"[Connect Dexcom]({dexcom_link})")

#========logging what you ate===========
st.subheader("Log What You Actually Ate")

with st.form("meal_log_form"):
    logged_protein = st.number_input("Protein eaten (g)", min_value=0)
    logged_carbs = st.number_input("Carbs eaten (g)", min_value=0)
    logged_fat = st.number_input("Fat eaten (g)", min_value=0)
    submitted = st.form_submit_button("Log Meal")

if submitted:
    actual = {"protein": logged_protein, "carbs": logged_carbs, "fat": logged_fat}
    st.success("Meal logged!")


#===========Recalculate GPT Meal Plan for Next Meal ==============
if submitted:
    actual = {"protein": logged_protein, "carbs": logged_carbs, "fat": logged_fat}
    remaining_macros = adjust_macros_for_next_meal(macros, actual)

    st.subheader("Recalculated Meal Plan")
    adjusted_plan = generate_meal_plan(remaining_macros, diet)
    st.markdown(adjusted_plan)

#===========End of Day Trigger==========
    st.subheader("End of Day Review")

if st.button("Recalculate Tomorrow’s Macros"):
    new_macros = adjust_next_day_macros(macros, actual, glucose_stability, recovery_score)
    st.write("Tomorrow’s AI-adjusted targets:")
    st.json(new_macros)




