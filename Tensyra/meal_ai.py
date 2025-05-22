# meal_ai.py
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_meal_plan(macros, dietary_preference):
    prompt = f"""
You are a clinical nutritionist. Generate a complete one-day meal plan that matches:

- Protein: {macros['protein']}g
- Carbohydrates: {macros['carbs']}g
- Fat: {macros['fat']}g

The user follows a {dietary_preference} diet and must avoid all major allergens, including gluten, soy, dairy, eggs, peanuts, shellfish, and tree nuts (unless specified as acceptable). Meals should promote stable blood glucose and high recovery, suitable for someone using a CGM and WHOOP recovery data.

Include:
- 3 main meals (breakfast, lunch, dinner)
- 2 optional snacks
- Ingredients, portion sizes, and estimated macros per meal
- A simple format (markdown or plain text)

Ensure the plan is balanced and practical.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ GPT Meal Plan Error: {str(e)}"
