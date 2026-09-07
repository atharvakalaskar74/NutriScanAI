# =========================================================
# NUTRISCAN AI — CONTEXT-AWARE NUTRITION CHATBOT SERVICE
# =========================================================
from datetime import datetime, date

def handle_chat_message(user_message, user_id, cursor=None, user_profile=None):
    """
    Answers user nutrition questions with real database grounding.
    Uses actual meal history and user goals from the database whenever relevant.
    """
    msg = (user_message or "").strip().lower()
    user_name = (user_profile or {}).get("name") or "there"
    goal = (user_profile or {}).get("goal") or "General Health"

    if not msg:
        return "Please enter a question about your nutrition, daily meals, or healthy eating!"

    # ---------------------------------------------------------
    # 1. QUERIES ABOUT TODAY'S INTAKE OR SPECIFIC MACROS
    # ---------------------------------------------------------
    is_today_query = any(w in msg for w in ["today", "so far", "my meals", "eaten"])
    wants_protein = "protein" in msg
    wants_calories = any(w in msg for w in ["calorie", "calories", "kcal"])
    wants_carbs = any(w in msg for w in ["carb", "carbs", "carbohydrate"])
    wants_fat = "fat" in msg
    wants_fiber = "fiber" in msg

    if cursor and (is_today_query or wants_protein or wants_calories or wants_carbs or wants_fat or wants_fiber):
        try:
            # Query today's totals and meals
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as meal_count,
                    COALESCE(SUM(calories), 0) AS total_calories,
                    COALESCE(SUM(protein), 0) AS total_protein,
                    COALESCE(SUM(carbohydrates), 0) AS total_carbs,
                    COALESCE(SUM(fat), 0) AS total_fat,
                    COALESCE(SUM(fiber), 0) AS total_fiber
                FROM meal_history
                WHERE user_id = %s AND DATE(created_at) = CURDATE()
                """,
                (user_id,)
            )
            totals = cursor.fetchone() or {}

            # Query names of today's meals
            cursor.execute(
                """
                SELECT food_name, calories, protein, created_at
                FROM meal_history
                WHERE user_id = %s AND DATE(created_at) = CURDATE()
                ORDER BY created_at ASC
                """,
                (user_id,)
            )
            today_meals = cursor.fetchall() or []

            meal_count = totals.get("meal_count", 0)
            cals = round(float(totals.get("total_calories", 0)), 1)
            prot = round(float(totals.get("total_protein", 0)), 1)
            carbs = round(float(totals.get("total_carbs", 0)), 1)
            fat = round(float(totals.get("total_fat", 0)), 1)
            fib = round(float(totals.get("total_fiber", 0)), 1)

            # Specific answers if asked
            if "protein" in msg and (is_today_query or "how much" in msg or "did i eat" in msg):
                if meal_count == 0:
                    return f"You haven't logged any meals today yet, {user_name}. Once you scan or log a meal, I will track your exact protein intake here!"
                meal_list = ", ".join([f"{m['food_name']} ({m['protein']}g)" for m in today_meals])
                return f"Today you have consumed **{prot}g of protein** across {meal_count} logged meal(s) ({meal_list})."

            if ("calorie" in msg or "calories" in msg) and (is_today_query or "how much" in msg or "did i eat" in msg):
                if meal_count == 0:
                    return f"You haven't logged any meals today yet, {user_name}. Your total calories logged today is 0 kcal."
                return f"Your total calorie intake today is **{cals} kcal** across {meal_count} logged meal(s)."

            if ("what did i eat" in msg or "my meals" in msg or "today's meals" in msg) or (is_today_query and "summary" in msg):
                if meal_count == 0:
                    return f"No meals logged today yet, {user_name}. Head over to **Scan Food** to snap a photo and record your first meal!"
                summary = f"Today you logged **{meal_count} meal(s)**:\n"
                for m in today_meals:
                    summary += f"• **{m['food_name'].title()}**: {m['calories']} kcal, {m['protein']}g protein\n"
                summary += f"\n**Daily Totals**: {cals} kcal | {prot}g Protein | {carbs}g Carbs | {fat}g Fat | {fib}g Fiber."
                return summary

        except Exception as e:
            print("Chatbot DB error:", e)

    # ---------------------------------------------------------
    # 2. QUERIES ABOUT RECENT MEALS OR TOTAL HISTORY
    # ---------------------------------------------------------
    if cursor and any(w in msg for w in ["history", "yesterday", "recent", "past meals", "last meal"]):
        try:
            cursor.execute(
                """
                SELECT food_name, calories, protein, created_at
                FROM meal_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 5
                """,
                (user_id,)
            )
            recent = cursor.fetchall() or []
            if not recent:
                return f"You don't have any recorded meals in your history yet, {user_name}."
            
            resp = "Here are your most recently logged meals:\n"
            for m in recent:
                t_str = m['created_at'].strftime("%b %d, %H:%M") if hasattr(m['created_at'], 'strftime') else str(m['created_at'])
                resp += f"• **{m['food_name'].title()}** ({t_str}): {m['calories']} kcal, {m['protein']}g protein\n"
            return resp
        except Exception as e:
            print("Chatbot history error:", e)

    # ---------------------------------------------------------
    # 3. USER PROFILE & GOAL QUESTIONS
    # ---------------------------------------------------------
    if any(w in msg for w in ["my goal", "target", "bmr", "tdee", "profile"]):
        goal_text = f"Your current goal is **{goal}**."
        if user_profile:
            wt = user_profile.get("weight")
            ht = user_profile.get("height")
            act = user_profile.get("activity_level")
            return (
                f"{goal_text}\n"
                f"• Height: {ht} cm | Weight: {wt} kg | Activity: {act}\n"
                f"You can review your personalized daily targets on your **Dashboard** or adjust them in your **Profile**."
            )
        return goal_text

    # ---------------------------------------------------------
    # 4. NUTRITION ADVICE & MEAL RECOMMENDATIONS
    # ---------------------------------------------------------
    if any(w in msg for w in ["recommend", "what should i eat", "suggest", "dinner", "lunch", "breakfast", "snack"]):
        if "lose" in goal.lower() or "loss" in goal.lower():
            return (
                "For your **weight loss** goal, focus on high-satiety, nutrient-dense options:\n"
                "• **Breakfast**: Vegetable poha, oats with boiled egg whites, or idli with sambar.\n"
                "• **Lunch**: Grilled chicken or paneer with a large green salad and 1-2 chapatis.\n"
                "• **Dinner**: Light dal tadka with steamed vegetables, or clear vegetable soup with grilled tofu.\n"
                "• **Snack**: Roasted chana, cucumber slices with hummus, or green tea with almonds."
            )
        elif "gain" in goal.lower() or "muscle" in goal.lower():
            return (
                "For your **muscle gain** goal, prioritize protein and clean complex carbohydrates:\n"
                "• **Breakfast**: 3 eggs (or paneer scramble) with whole grain toast and banana.\n"
                "• **Lunch**: Chicken Biryani or Rajma Rice with curd and salad.\n"
                "• **Dinner**: Paneer Tikka or grilled chicken curry with dal and brown rice.\n"
                "• **Post-workout**: Whey protein shake or sattu drink with a handful of nuts."
            )
        else:
            return (
                "For a **balanced, healthy diet**:\n"
                "• Aim to fill half your plate with colorful vegetables and salads.\n"
                "• Include a clean protein source (dal, eggs, paneer, chicken, tofu) in every meal.\n"
                "• Opt for whole grains (whole wheat chapati, brown rice, oats) over refined carbs."
            )

    if "protein" in msg:
        return (
            "**High-Quality Protein Sources**:\n"
            "• **Vegetarian**: Paneer (18-22g/100g), Greek yogurt / curd (10g/100g), Dal & lentils (9g/cooked cup), Tofu (10g/100g), Sattu.\n"
            "• **Non-Vegetarian**: Chicken breast (31g/100g), Eggs (6g per large egg), Fish (20-25g/100g).\n"
            "Tip: Distribute your protein across 3–4 meals to maximize absorption!"
        )

    if "fiber" in msg:
        return (
            "**Great Dietary Fiber Sources**:\n"
            "• Oats, kidney beans (rajma), chickpeas (chole), yellow lentils.\n"
            "• Vegetables: Spinach, broccoli, carrots, green peas.\n"
            "• Fruits: Apples, berries, pears, and oranges.\n"
            "Daily goal: Aim for 25–35 grams of fiber daily for optimal digestion and cholesterol regulation."
        )

    if any(w in msg for w in ["water", "hydrate", "hydration"]):
        return "Staying well-hydrated is crucial for metabolic function! Aim for 2.5 to 3.5 liters of water daily, especially when consuming protein and dietary fiber."

    # ---------------------------------------------------------
    # 5. GREETING & DEFAULT HELPFUL RESPONSE
    # ---------------------------------------------------------
    if any(w in msg for w in ["hi", "hello", "hey", "who are you"]):
        return (
            f"Hello {user_name}! 👋 I am your **NutriScan AI Nutrition Assistant**.\n"
            "Here are a few things you can ask me:\n"
            "• *How much protein have I eaten today?*\n"
            "• *What are my total calories today?*\n"
            "• *What did I eat today?*\n"
            "• *Show my recent meals*\n"
            "• *Suggest a healthy meal for my goal*"
        )

    return (
        f"I'm here to help with your nutrition, {user_name}! You can ask me about your logged meals today "
        "(e.g., 'How much protein did I eat today?', 'Today's calories'), your recent meal history, "
        "or general dietary guidance for your goal."
    )
