# logic.py
import numpy as np

def calculate_mas_score(glucose_data, recovery_score, hrv_score, sleep_score, macro_adherence, symptoms_score):
    # Normalize and weight each metric (weights can be tuned over time)
    weights = {
        "glucose": 0.25,
        "recovery": 0.2,
        "hrv": 0.15,
        "sleep": 0.15,
        "macro": 0.15,
        "symptoms": 0.1
    }

    mas_score = (
        weights["glucose"] * glucose_data +
        weights["recovery"] * recovery_score +
        weights["hrv"] * hrv_score +
        weights["sleep"] * sleep_score +
        weights["macro"] * macro_adherence +
        weights["symptoms"] * symptoms_score
    )

    return round(mas_score, 2)

def analyze_glucose(glucose_values):
    """
    Expects a list of glucose values over time.
    Returns:
    - Stability score (0–100)
    - Flags for spikes or crashes
    """
    if not glucose_values:
        return 0, []

    std_dev = np.std(glucose_values)
    max_val = max(glucose_values)
    min_val = min(glucose_values)

    stability_score = max(0, 100 - std_dev * 2)
    flags = []

    if max_val > 180:
        flags.append("Spike")
    if min_val < 70:
        flags.append("Crash")
    if std_dev > 25:
        flags.append("High Variability")

    return round(stability_score, 2), flags

def calculate_macros(weight_kg, goal, recovery_score, glucose_stability_score):
    """
    Returns macros based on adaptive AI logic.
    """
    protein = 2.0 * weight_kg

    # Adjust carbs based on glucose control + recovery
    if recovery_score < 50 or glucose_stability_score < 60:
        carb_factor = 1.0 if goal == "maintain" else 0.8 if goal == "cut" else 1.2
    else:
        carb_factor = 2.0 if goal == "gain" else 1.6 if goal == "maintain" else 1.2

    carbs = carb_factor * weight_kg
    fat = (0.8 if goal == "cut" else 1.0) * weight_kg

    return {
        "protein": round(protein),
        "carbs": round(carbs),
        "fat": round(fat)
    }


#=======Recalculation Logic=========
def adjust_macros_for_next_meal(original, actual):
    diff = {
        "protein": original["protein"] - actual["protein"],
        "carbs": original["carbs"] - actual["carbs"],
        "fat": original["fat"] - actual["fat"]
    }

    # Prevent negatives — assume overage is absorbed
    for key in diff:
        diff[key] = max(0, diff[key])

    return diff

#==========auto-Recalculated Daily Targets==========
def adjust_next_day_macros(yesterday_macros, logged_macros, glucose_stability_score, recovery_score):
    diff = {
        "protein": logged_macros['protein'] - yesterday_macros['protein'],
        "carbs": logged_macros['carbs'] - yesterday_macros['carbs'],
        "fat": logged_macros['fat'] - yesterday_macros['fat']
    }

    # Adjust rules
    protein_adj = 0
    carb_adj = 0
    fat_adj = 0

    if diff['protein'] < -20:
        protein_adj += 10
    if diff['carbs'] < -30 and glucose_stability_score > 80 and recovery_score > 70:
        carb_adj += 20
    if glucose_stability_score < 50 or recovery_score < 40:
        carb_adj -= 15

    return {
        "protein": max(0, yesterday_macros['protein'] + protein_adj),
        "carbs": max(0, yesterday_macros['carbs'] + carb_adj),
        "fat": max(0, yesterday_macros['fat'] + fat_adj)
    }
