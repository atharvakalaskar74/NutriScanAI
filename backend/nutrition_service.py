# =========================================================
# NUTRISCAN AI — NUTRITION & HEALTH SCORE SERVICE
# =========================================================
import math

# Reference database for verified nutritional content per standard serving
# Extends and compliments the MySQL food_items table
REFERENCE_FOODS = {
    "chicken biryani": {
        "food_name": "Chicken Biryani",
        "serving_size": "1 plate (350g)",
        "calories": 520.0,
        "protein": 24.0,
        "carbohydrates": 62.0,
        "fat": 18.0,
        "fiber": 3.5,
        "sugar": 3.0,
        "sodium": 680.0,
        "ingredients": "Basmati rice, chicken, yogurt, onions, whole spices, saffron, ghee"
    },
    "vegetable biryani": {
        "food_name": "Vegetable Biryani",
        "serving_size": "1 plate (300g)",
        "calories": 380.0,
        "protein": 9.0,
        "carbohydrates": 65.0,
        "fat": 10.0,
        "fiber": 6.5,
        "sugar": 4.0,
        "sodium": 520.0,
        "ingredients": "Basmati rice, mixed vegetables (peas, carrots, beans), spices, mint"
    },
    "mutton biryani": {
        "food_name": "Mutton Biryani",
        "serving_size": "1 plate (350g)",
        "calories": 610.0,
        "protein": 28.0,
        "carbohydrates": 60.0,
        "fat": 28.0,
        "fiber": 3.0,
        "sugar": 3.0,
        "sodium": 740.0,
        "ingredients": "Rice, tender mutton chunks, ghee, saffron, fried onions, spices"
    },
    "fried rice": {
        "food_name": "Fried Rice",
        "serving_size": "1 plate (250g)",
        "calories": 400.0,
        "protein": 10.0,
        "carbohydrates": 60.0,
        "fat": 14.0,
        "fiber": 3.0,
        "sugar": 3.5,
        "sodium": 650.0,
        "ingredients": "Cooked rice, carrots, bell peppers, soy sauce, garlic, spring onions"
    },
    "pulao": {
        "food_name": "Veg Pulao",
        "serving_size": "1 plate (250g)",
        "calories": 310.0,
        "protein": 7.0,
        "carbohydrates": 54.0,
        "fat": 7.5,
        "fiber": 4.0,
        "sugar": 2.5,
        "sodium": 420.0,
        "ingredients": "Basmati rice, green peas, cumin, cloves, cardamom, light ghee"
    },
    "butter chicken": {
        "food_name": "Butter Chicken",
        "serving_size": "1 bowl (200g)",
        "calories": 440.0,
        "protein": 26.0,
        "carbohydrates": 12.0,
        "fat": 32.0,
        "fiber": 2.0,
        "sugar": 6.0,
        "sodium": 780.0,
        "ingredients": "Grilled chicken, tomato puree, heavy cream, butter, fenugreek, spices"
    },
    "chicken curry": {
        "food_name": "Chicken Curry",
        "serving_size": "1 bowl (220g)",
        "calories": 340.0,
        "protein": 28.0,
        "carbohydrates": 8.0,
        "fat": 22.0,
        "fiber": 2.5,
        "sugar": 3.0,
        "sodium": 620.0,
        "ingredients": "Chicken, onions, tomatoes, ginger-garlic paste, coriander, spices"
    },
    "dal": {
        "food_name": "Dal Tadka",
        "serving_size": "1 bowl (200g)",
        "calories": 190.0,
        "protein": 11.0,
        "carbohydrates": 26.0,
        "fat": 5.0,
        "fiber": 7.0,
        "sugar": 1.5,
        "sodium": 410.0,
        "ingredients": "Yellow lentils (Toor dal), tomatoes, garlic, cumin, ghee tempering"
    },
    "paneer tikka": {
        "food_name": "Paneer Tikka",
        "serving_size": "150g (6 cubes)",
        "calories": 320.0,
        "protein": 22.0,
        "carbohydrates": 10.0,
        "fat": 22.0,
        "fiber": 2.5,
        "sugar": 3.0,
        "sodium": 500.0,
        "ingredients": "Cottage cheese (paneer), yogurt marinade, bell peppers, onions, chaat masala"
    },
    "palak paneer": {
        "food_name": "Palak Paneer",
        "serving_size": "1 bowl (220g)",
        "calories": 290.0,
        "protein": 16.0,
        "carbohydrates": 11.0,
        "fat": 20.0,
        "fiber": 5.0,
        "sugar": 2.0,
        "sodium": 540.0,
        "ingredients": "Fresh spinach puree, paneer cubes, garlic, cumin, light cream"
    },
    "samosa": {
        "food_name": "Samosa",
        "serving_size": "2 pieces (120g)",
        "calories": 260.0,
        "protein": 6.0,
        "carbohydrates": 30.0,
        "fat": 13.0,
        "fiber": 3.0,
        "sugar": 2.0,
        "sodium": 450.0,
        "ingredients": "Crisp flour pastry, spiced potato and pea filling, deep-fried"
    },
    "dosa": {
        "food_name": "Masala Dosa",
        "serving_size": "1 dosa (120g)",
        "calories": 210.0,
        "protein": 5.0,
        "carbohydrates": 34.0,
        "fat": 6.5,
        "fiber": 3.0,
        "sugar": 1.5,
        "sodium": 360.0,
        "ingredients": "Fermented rice & urad dal batter, spiced mashed potato stuffing"
    },
    "idli": {
        "food_name": "Idli",
        "serving_size": "2 pieces (120g)",
        "calories": 140.0,
        "protein": 5.0,
        "carbohydrates": 28.0,
        "fat": 1.0,
        "fiber": 2.0,
        "sugar": 1.0,
        "sodium": 300.0,
        "ingredients": "Steamed fermented rice and black gram (urad dal)"
    },
    "poha": {
        "food_name": "Poha",
        "serving_size": "1 bowl (150g)",
        "calories": 250.0,
        "protein": 5.0,
        "carbohydrates": 40.0,
        "fat": 8.0,
        "fiber": 3.0,
        "sugar": 2.0,
        "sodium": 350.0,
        "ingredients": "Flattened rice, mustard seeds, onions, potatoes, turmeric, peanuts"
    },
    "upma": {
        "food_name": "Upma",
        "serving_size": "1 bowl (200g)",
        "calories": 220.0,
        "protein": 6.0,
        "carbohydrates": 35.0,
        "fat": 7.0,
        "fiber": 4.0,
        "sugar": 2.0,
        "sodium": 300.0,
        "ingredients": "Semolina (rava), ginger, mustard seeds, curry leaves, vegetables"
    },
    "chapati": {
        "food_name": "Chapati",
        "serving_size": "2 pieces (80g)",
        "calories": 160.0,
        "protein": 6.0,
        "carbohydrates": 30.0,
        "fat": 3.0,
        "fiber": 4.0,
        "sugar": 1.0,
        "sodium": 180.0,
        "ingredients": "Whole wheat flour (atta), water, touch of oil or ghee"
    },
    "dal rice": {
        "food_name": "Dal Rice",
        "serving_size": "1 plate (300g)",
        "calories": 400.0,
        "protein": 14.0,
        "carbohydrates": 65.0,
        "fat": 8.0,
        "fiber": 8.0,
        "sugar": 3.0,
        "sodium": 400.0,
        "ingredients": "Steamed white rice, yellow dal tadka, cumin, ghee"
    },
    "vada pav": {
        "food_name": "Vada Pav",
        "serving_size": "1 piece (130g)",
        "calories": 290.0,
        "protein": 7.0,
        "carbohydrates": 40.0,
        "fat": 11.0,
        "fiber": 3.0,
        "sugar": 5.0,
        "sodium": 550.0,
        "ingredients": "Spiced potato dumpling fried in gram flour, pav bread, chutneys"
    },
    "pav bhaji": {
        "food_name": "Pav Bhaji",
        "serving_size": "1 plate (bhaji + 2 pav)",
        "calories": 410.0,
        "protein": 10.0,
        "carbohydrates": 56.0,
        "fat": 16.0,
        "fiber": 7.0,
        "sugar": 6.0,
        "sodium": 650.0,
        "ingredients": "Mashed mixed vegetables, butter, pav bhaji masala, buttered bread rolls"
    },
    "rajma rice": {
        "food_name": "Rajma Rice",
        "serving_size": "1 plate (300g)",
        "calories": 420.0,
        "protein": 15.0,
        "carbohydrates": 70.0,
        "fat": 9.0,
        "fiber": 10.0,
        "sugar": 4.0,
        "sodium": 450.0,
        "ingredients": "Kidney beans in rich tomato-onion gravy, steamed basmati rice"
    },
    "pizza": {
        "food_name": "Pizza",
        "serving_size": "2 slices (200g)",
        "calories": 520.0,
        "protein": 20.0,
        "carbohydrates": 58.0,
        "fat": 24.0,
        "fiber": 3.0,
        "sugar": 6.0,
        "sodium": 900.0,
        "ingredients": "Wheat crust, pizza sauce, mozzarella cheese, herbs, olive oil"
    },
    "burger": {
        "food_name": "Burger",
        "serving_size": "1 burger (180g)",
        "calories": 450.0,
        "protein": 25.0,
        "carbohydrates": 40.0,
        "fat": 22.0,
        "fiber": 3.0,
        "sugar": 7.0,
        "sodium": 800.0,
        "ingredients": "Bun, patty, lettuce, tomato, cheese slice, condiments"
    },
    "noodles": {
        "food_name": "Noodles",
        "serving_size": "1 bowl (200g)",
        "calories": 360.0,
        "protein": 9.0,
        "carbohydrates": 52.0,
        "fat": 13.0,
        "fiber": 3.5,
        "sugar": 4.0,
        "sodium": 720.0,
        "ingredients": "Wheat or egg noodles, cabbage, carrots, soy sauce, garlic, sesame oil"
    },
    "pasta": {
        "food_name": "Pasta",
        "serving_size": "1 bowl (220g)",
        "calories": 380.0,
        "protein": 14.0,
        "carbohydrates": 55.0,
        "fat": 12.0,
        "fiber": 4.0,
        "sugar": 6.0,
        "sodium": 500.0,
        "ingredients": "Semolina pasta, marinara or white sauce, olive oil, parmesan, herbs"
    },
    "salad": {
        "food_name": "Fresh Green Salad",
        "serving_size": "1 bowl (180g)",
        "calories": 140.0,
        "protein": 4.0,
        "carbohydrates": 14.0,
        "fat": 7.0,
        "fiber": 5.0,
        "sugar": 4.5,
        "sodium": 220.0,
        "ingredients": "Lettuce, cucumber, cherry tomatoes, bell pepper, olive oil lemon dressing"
    },
    "sandwich": {
        "food_name": "Veg Grilled Sandwich",
        "serving_size": "1 sandwich (160g)",
        "calories": 280.0,
        "protein": 8.0,
        "carbohydrates": 42.0,
        "fat": 9.0,
        "fiber": 4.5,
        "sugar": 4.0,
        "sodium": 480.0,
        "ingredients": "Whole wheat bread, potato, cucumber, tomato, green chutney, cheese"
    },
    "omelette": {
        "food_name": "Egg Omelette",
        "serving_size": "2 eggs (120g)",
        "calories": 220.0,
        "protein": 14.0,
        "carbohydrates": 3.0,
        "fat": 16.0,
        "fiber": 1.0,
        "sugar": 1.5,
        "sodium": 340.0,
        "ingredients": "2 whole eggs, onions, green chilies, coriander, salt, cooking oil"
    },
    "chole bhature": {
        "food_name": "Chole Bhature",
        "serving_size": "1 plate (2 bhature + chole)",
        "calories": 580.0,
        "protein": 16.0,
        "carbohydrates": 74.0,
        "fat": 25.0,
        "fiber": 9.0,
        "sugar": 5.0,
        "sodium": 760.0,
        "ingredients": "Spicy chickpea curry, deep-fried leavened bread (bhatura), pickle, onions"
    }
}


def get_nutrition_data(food_name, db_cursor=None, quantity=1.0):
    """
    Retrieves full nutrition information for a food item.
    Checks the MySQL database first. If not found or if db_cursor is None,
    falls back to the comprehensive reference nutrition database.
    """
    clean_name = food_name.strip().lower()
    nutrition = None

    if db_cursor:
        try:
            # Query MySQL food_items table
            db_cursor.execute(
                """
                SELECT * FROM food_items
                WHERE LOWER(%s) LIKE CONCAT('%%', LOWER(food_name), '%%')
                   OR LOWER(food_name) LIKE CONCAT('%%', LOWER(%s), '%%')
                LIMIT 1
                """,
                (clean_name, clean_name)
            )
            row = db_cursor.fetchone()
            if row:
                nutrition = dict(row)
        except Exception as e:
            print("DB nutrition lookup error:", e)

    # If not in DB or incomplete, check reference dictionary
    if not nutrition:
        for key, ref in REFERENCE_FOODS.items():
            if key in clean_name or clean_name in key:
                nutrition = dict(ref)
                nutrition["id"] = None
                break

    # If still not found, create a sensible default nutritional profile
    if not nutrition:
        nutrition = {
            "id": None,
            "food_name": food_name.title(),
            "serving_size": "1 serving",
            "calories": 320.0,
            "protein": 10.0,
            "carbohydrates": 45.0,
            "fat": 11.0,
            "fiber": 3.0,
            "sugar": 3.0,
            "sodium": 450.0,
            "ingredients": "Standard dietary preparation"
        }

    # Ensure all nutritional keys exist
    defaults = {
        "calories": 300.0,
        "protein": 10.0,
        "carbohydrates": 40.0,
        "fat": 10.0,
        "fiber": 3.0,
        "sugar": 3.0,
        "sodium": 400.0,
        "serving_size": "1 serving",
        "ingredients": "Assorted standard ingredients"
    }
    for k, v in defaults.items():
        if k not in nutrition or nutrition[k] is None:
            nutrition[k] = v

    # Add ingredients if missing
    if "ingredients" not in nutrition:
        for key, ref in REFERENCE_FOODS.items():
            if key in clean_name or clean_name in key:
                nutrition["ingredients"] = ref.get("ingredients", "")
                break
        if not nutrition.get("ingredients"):
            nutrition["ingredients"] = "Fresh ingredients, seasonings, and natural spices"

    # Scale by quantity
    qty = max(float(quantity), 0.1)
    if qty != 1.0:
        scaled = dict(nutrition)
        for key in ["calories", "protein", "carbohydrates", "fat", "fiber", "sugar", "sodium"]:
            scaled[key] = round(float(scaled[key]) * qty, 1)
        scaled["quantity"] = qty
        return scaled

    nutrition["quantity"] = 1.0
    return nutrition


def calculate_health_score(nutrition):
    """
    Computes an explainable 0–100 Health Score based on nutrient densities:
    - Base: 70
    - Positive factors: High protein ratio, high dietary fiber
    - Penalties: High sodium (>600mg), high sugar (>10g), high saturated/total fat (>22g), excessive calories (>600kcal)
    - Returns: dict with score, category, color, explanation
    """
    calories = float(nutrition.get("calories") or 0)
    protein = float(nutrition.get("protein") or 0)
    carbs = float(nutrition.get("carbohydrates") or 0)
    fat = float(nutrition.get("fat") or 0)
    fiber = float(nutrition.get("fiber") or 0)
    sugar = float(nutrition.get("sugar") or 0)
    sodium = float(nutrition.get("sodium") or 0)

    score = 70.0
    reasons = []

    # 1. Protein evaluation
    if protein >= 20:
        score += 12
        reasons.append("High protein content supports muscle health")
    elif protein >= 10:
        score += 6
        reasons.append("Good protein content")
    else:
        score -= 4

    # 2. Fiber evaluation
    if fiber >= 6:
        score += 12
        reasons.append("Excellent dietary fiber for gut health")
    elif fiber >= 3:
        score += 6
        reasons.append("Decent fiber source")
    else:
        score -= 5

    # 3. Sodium evaluation
    if sodium > 800:
        score -= 16
        reasons.append("High sodium content (keep hydration high)")
    elif sodium > 550:
        score -= 8
        reasons.append("Moderate to high sodium")
    elif sodium <= 350:
        score += 5
        reasons.append("Low sodium")

    # 4. Sugar evaluation
    if sugar > 15:
        score -= 14
        reasons.append("High sugar content")
    elif sugar > 8:
        score -= 6
        reasons.append("Contains noticeable sugar")
    elif sugar <= 3:
        score += 4

    # 5. Fat evaluation
    if fat > 25:
        score -= 12
        reasons.append("High fat density; consume mindfully")
    elif fat > 18:
        score -= 6
    elif 3 <= fat <= 12:
        score += 4
        reasons.append("Balanced healthy fat level")

    # 6. Caloric balance
    if calories > 650:
        score -= 10
        reasons.append("High-calorie meal")
    elif 150 <= calories <= 450:
        score += 5
        reasons.append("Moderate calorie density")

    # Clamp score strictly between 15 and 98
    final_score = int(max(15, min(98, round(score))))

    if not reasons:
        reasons.append("Standard balanced nutritional profile")

    explanation = "; ".join(reasons[:3]) + "."

    # Quality category
    if final_score >= 80:
        category = "Very Healthy"
        color = "#238636"
    elif final_score >= 60:
        category = "Balanced"
        color = "#2da44e"
    elif final_score >= 40:
        category = "Moderate"
        color = "#d97706"
    else:
        category = "Indulgent / High Caution"
        color = "#dc2626"

    return {
        "score": final_score,
        "category": category,
        "color": color,
        "explanation": explanation
    }


def generate_nutrition_insights(food_name, nutrition, user_profile=None):
    """
    Generates tailored AI nutrition insights and recommendations
    based on nutritional attributes and user fitness goals.
    """
    user_profile = user_profile or {}
    goal = str(user_profile.get("goal") or "").lower()
    calories = float(nutrition.get("calories") or 0)
    protein = float(nutrition.get("protein") or 0)
    fat = float(nutrition.get("fat") or 0)
    fiber = float(nutrition.get("fiber") or 0)
    sodium = float(nutrition.get("sodium") or 0)
    sugar = float(nutrition.get("sugar") or 0)

    insights = []
    recommendations = []

    # Goal-oriented insights
    if "lose" in goal or "weight loss" in goal:
        if calories > 450:
            insights.append(f"{food_name.title()} is energy-dense ({calories:.0f} kcal).")
            recommendations.append("Pair with a large side salad or steamed vegetables to stay full without extra calories.")
        else:
            insights.append(f"Great fit for a calorie-conscious diet ({calories:.0f} kcal).")
            recommendations.append("Keep your next meal light to stay within your daily calorie target.")
    elif "gain" in goal or "muscle" in goal:
        if protein >= 18:
            insights.append(f"Excellent protein yield ({protein:.1f}g) to support muscle protein synthesis.")
            recommendations.append("Ideal as a post-workout recovery meal or core lunch option.")
        else:
            insights.append("Protein content is lower than ideal for a muscle-gain regimen.")
            recommendations.append("Consider topping with paneer, tofu, boiled eggs, or Greek yogurt.")
    else:
        insights.append(f"{food_name.title()} provides {calories:.0f} kcal with {protein:.1f}g protein.")
        recommendations.append("Maintain meal balance by staying hydrated and keeping sodium moderate.")

    # Nutrient-specific checks
    if fiber < 3:
        recommendations.append("Add whole grains, lentils, or fresh fruit to boost your daily fiber intake.")
    if sodium > 600:
        recommendations.append("Sodium is high. Drink plenty of water and choose low-sodium foods for your next meal.")
    if sugar > 8:
        recommendations.append("Contains noticeable sugar. Avoid sweetened beverages alongside this meal.")

    return {
        "message": " ".join(insights),
        "recommendation": " ".join(recommendations[:2])
    }
