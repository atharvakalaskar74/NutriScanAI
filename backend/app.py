from flask import Flask, request, render_template, jsonify, redirect, url_for, session, flash, send_from_directory
from database import get_db
from ai_model import recognize_food
from nutrition_service import get_nutrition_data, calculate_health_score, generate_nutrition_insights
from chatbot_service import handle_chat_message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import sys

# Ensure UTF-8 stdout/stderr on Windows consoles to prevent UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, "templates")

app = Flask(__name__, template_folder=template_dir)

# Secret key for login sessions
app.secret_key = os.getenv("FLASK_SECRET_KEY") or "nutriscan-dev-secret-key-change-this"

is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("NETLIFY"))
UPLOAD_FOLDER = "/tmp/uploads" if is_serverless else os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload size
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)



# =========================================================
# LOGIN REQUIRED DECORATOR
# =========================================================

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Basic validation
        if not name or not email or not password:
            flash("Please fill all required fields.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must contain at least 6 characters.", "error")
            return render_template("register.html")

        db = None
        cursor = None

        try:

            db = get_db()
            cursor = db.cursor(dictionary=True)

            # Check whether email already exists
            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                flash("An account with this email already exists.", "error")

                return render_template("register.html")

            # Hash password
            hashed_password = generate_password_hash(password)

            # Insert user
            cursor.execute(
                """
                INSERT INTO users
                (name, email, password)
                VALUES (%s, %s, %s)
                """,
                (name, email, hashed_password)
            )

            db.commit()

            flash("Registration successful! Please login.", "success")

            return redirect(url_for("login"))

        except Exception as e:

            print("Registration error:", e)

            flash("Registration failed. Please try again.", "error")

            return render_template("register.html")

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    return render_template("register.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:

            flash("Please enter email and password.", "error")

            return render_template("login.html")

        db = None
        cursor = None

        try:

            db = get_db()
            cursor = db.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                LIMIT 1
                """,
                (email,)
            )

            user = cursor.fetchone()

            if user and check_password_hash(user["password"], password):

                # Create session
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["user_email"] = user["email"]

                return redirect(url_for("dashboard"))

            flash("Invalid email or password.", "error")

        except Exception as e:

            print("Login error:", e)

            flash("Login failed. Please try again.", "error")

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    return render_template("login.html")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Get today's nutrition totals & meal count
        cursor.execute(
            """
            SELECT
                COUNT(*) AS meal_count,
                COALESCE(SUM(calories), 0) AS calories,
                COALESCE(SUM(protein), 0) AS protein,
                COALESCE(SUM(carbohydrates), 0) AS carbohydrates,
                COALESCE(SUM(fat), 0) AS fat,
                COALESCE(SUM(fiber), 0) AS fiber
            FROM meal_history
            WHERE user_id = %s
              AND DATE(created_at) = CURDATE()
            """,
            (session["user_id"],)
        )

        today = cursor.fetchone() or {}

        # Get today's meals to calculate today's average health score
        cursor.execute(
            """
            SELECT calories, protein, carbohydrates, fat, fiber
            FROM meal_history
            WHERE user_id = %s
              AND DATE(created_at) = CURDATE()
            """,
            (session["user_id"],)
        )
        today_meals = cursor.fetchall() or []
        if today_meals:
            scores = [calculate_health_score(m)["score"] for m in today_meals]
            today_health_score = round(sum(scores) / len(scores))
        else:
            today_health_score = 0

        # Get recent meals across history
        cursor.execute(
            """
            SELECT
                id,
                food_name,
                calories,
                protein,
                carbohydrates,
                fat,
                fiber,
                image_path,
                meal_type,
                created_at
            FROM meal_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 6
            """,
            (session["user_id"],)
        )
        recent_meals = cursor.fetchall() or []
        for m in recent_meals:
            m["health_score"] = calculate_health_score(m)
            if m.get("image_path"):
                m["image_url"] = f"/uploads/{os.path.basename(m['image_path'])}"
            else:
                m["image_url"] = None

        # Get user profile
        cursor.execute(
            """
            SELECT age, height, weight, gender, activity_level, goal
            FROM users
            WHERE id = %s
            LIMIT 1
            """,
            (session["user_id"],)
        )

        user = cursor.fetchone()

        # Default daily goals
        calorie_goal = 2000
        protein_goal = 60
        carb_goal = 250
        fat_goal = 65
        fiber_goal = 30

        # Calculate calories from user's profile
        if user and all([
            user.get("age"),
            user.get("height"),
            user.get("weight"),
            user.get("gender")
        ]):

            age = float(user["age"])
            height = float(user["height"])
            weight = float(user["weight"])

            if str(user["gender"]).lower() == "male":
                bmr = (
                    10 * weight
                    + 6.25 * height
                    - 5 * age
                    + 5
                )
            else:
                bmr = (
                    10 * weight
                    + 6.25 * height
                    - 5 * age
                    - 161
                )

            activity_factors = {
                "Sedentary": 1.20,
                "Lightly Active": 1.375,
                "Moderately Active": 1.55,
                "Very Active": 1.725
            }

            factor = activity_factors.get(
                user.get("activity_level"),
                1.20
            )

            calorie_goal = round(bmr * factor)

            # Goals aligned with user goal
            user_goal = str(user.get("goal") or "").lower()
            if "lose" in user_goal:
                calorie_goal = max(1400, calorie_goal - 400)
                protein_goal = round(weight * 1.2)
                carb_goal = round((calorie_goal * 0.40) / 4)
                fat_goal = round((calorie_goal * 0.25) / 9)
            elif "gain" in user_goal:
                calorie_goal = calorie_goal + 350
                protein_goal = round(weight * 1.6)
                carb_goal = round((calorie_goal * 0.50) / 4)
                fat_goal = round((calorie_goal * 0.25) / 9)
            else:
                protein_goal = round(weight * 1.0)
                carb_goal = round((calorie_goal * 0.50) / 4)
                fat_goal = round((calorie_goal * 0.30) / 9)

        return render_template(
            "dashboard.html",
            user_name=session.get("user_name"),
            today=today,
            today_health_score=today_health_score,
            recent_meals=recent_meals,
            calorie_goal=calorie_goal,
            protein_goal=protein_goal,
            carb_goal=carb_goal,
            fat_goal=fat_goal,
            fiber_goal=fiber_goal
        )

    except Exception as e:

        print("Dashboard error:", e)

        return render_template(
            "dashboard.html",
            user_name=session.get("user_name"),
            today={
                "meal_count": 0,
                "calories": 0,
                "protein": 0,
                "carbohydrates": 0,
                "fat": 0,
                "fiber": 0
            },
            today_health_score=0,
            recent_meals=[],
            calorie_goal=2000,
            protein_goal=60,
            carb_goal=250,
            fat_goal=65,
            fiber_goal=30
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()

@app.route("/scan-food")
@login_required
def scan_food():

    return render_template("index.html")

@app.route("/meal-history")
@login_required
def meal_history():

    db = None
    cursor = None

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                m.id,
                m.food_name,
                m.quantity,
                m.calories,
                m.protein,
                m.carbohydrates,
                m.fat,
                m.fiber,
                m.image_path,
                m.meal_type,
                m.created_at,
                a.ai_message,
                a.recommendation
            FROM meal_history m
            LEFT JOIN ai_analysis a ON a.meal_id = m.id
            WHERE m.user_id = %s
            ORDER BY m.created_at DESC
            """,
            (session["user_id"],)
        )

        meals = cursor.fetchall() or []
        for m in meals:
            m["health_score"] = calculate_health_score(m)
            if m.get("image_path"):
                m["image_url"] = f"/uploads/{os.path.basename(m['image_path'])}"
            else:
                m["image_url"] = None

        return render_template(
            "meal_history.html",
            meals=meals
        )

    except Exception as e:

        print("Meal history error:", e)

        return render_template(
            "meal_history.html",
            meals=[]
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()

# =========================================================
# PROFILE
# =========================================================

# =========================================================
# USER PROFILE
# =========================================================

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # -------------------------------------------------
        # GET CURRENT USER
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE id = %s
            LIMIT 1
            """,
            (session["user_id"],)
        )

        user = cursor.fetchone()

        if not user:

            session.clear()

            return redirect(url_for("login"))


        # -------------------------------------------------
        # SAVE PROFILE
        # -------------------------------------------------

        if request.method == "POST":

            age = request.form.get("age")
            height = request.form.get("height")
            weight = request.form.get("weight")
            gender = request.form.get("gender")
            activity_level = request.form.get("activity_level")
            goal = request.form.get("goal")


            # Check empty fields

            if not all([
                age,
                height,
                weight,
                gender,
                activity_level,
                goal
            ]):

                flash(
                    "Please fill all profile fields.",
                    "error"
                )

                return render_template(
                    "profile.html",
                    user=user
                )


            # Convert numeric values

            try:

                age = int(age)
                height = float(height)
                weight = float(weight)

            except ValueError:

                flash(
                    "Please enter valid numeric values.",
                    "error"
                )

                return render_template(
                    "profile.html",
                    user=user
                )


            # -------------------------------------------------
            # VALIDATION
            # -------------------------------------------------

            if age <= 0 or age > 120:

                flash(
                    "Please enter a valid age.",
                    "error"
                )

                return render_template(
                    "profile.html",
                    user=user
                )


            if height <= 0 or height > 250:

                flash(
                    "Please enter a valid height.",
                    "error"
                )

                return render_template(
                    "profile.html",
                    user=user
                )


            if weight <= 0 or weight > 300:

                flash(
                    "Please enter a valid weight.",
                    "error"
                )

                return render_template(
                    "profile.html",
                    user=user
                )


            # -------------------------------------------------
            # UPDATE DATABASE
            # -------------------------------------------------

            cursor.execute(
                """
                UPDATE users
                SET age = %s,
                    height = %s,
                    weight = %s,
                    gender = %s,
                    activity_level = %s,
                    goal = %s
                WHERE id = %s
                """,
                (
                    age,
                    height,
                    weight,
                    gender,
                    activity_level,
                    goal,
                    session["user_id"]
                )
            )

            db.commit()


            # Update local user object

            user["age"] = age
            user["height"] = height
            user["weight"] = weight
            user["gender"] = gender
            user["activity_level"] = activity_level
            user["goal"] = goal


            flash(
                "Profile updated successfully!",
                "success"
            )


        # =====================================================
        # BMI CALCULATION
        # =====================================================

        bmi = None
        bmi_category = None


        if user.get("height") and user.get("weight"):

            height_m = float(user["height"]) / 100

            if height_m > 0:

                bmi = round(
                    float(user["weight"]) /
                    (height_m * height_m),
                    2
                )


                if bmi < 18.5:

                    bmi_category = "Underweight"

                elif bmi < 25:

                    bmi_category = "Normal Weight"

                elif bmi < 30:

                    bmi_category = "Overweight"

                else:

                    bmi_category = "Obesity"


        # =====================================================
        # BMR CALCULATION
        # Mifflin-St Jeor Equation
        # =====================================================

        bmr = None

        if (
            user.get("age")
            and user.get("height")
            and user.get("weight")
            and user.get("gender")
        ):

            age_value = float(user["age"])
            height_value = float(user["height"])
            weight_value = float(user["weight"])


            if str(user["gender"]).lower() == "male":

                bmr = (
                    10 * weight_value
                    + 6.25 * height_value
                    - 5 * age_value
                    + 5
                )

            else:

                bmr = (
                    10 * weight_value
                    + 6.25 * height_value
                    - 5 * age_value
                    - 161
                )


            bmr = round(bmr)


        # =====================================================
        # TDEE CALCULATION
        # =====================================================

        tdee = None

        activity_factors = {

            "Sedentary": 1.20,

            "Lightly Active": 1.375,

            "Moderately Active": 1.55,

            "Very Active": 1.725

        }


        if bmr and user.get("activity_level"):

            factor = activity_factors.get(
                user["activity_level"],
                1.20
            )

            tdee = round(
                bmr * factor
            )


        # =====================================================
        # SEND DATA TO HTML
        # =====================================================

        return render_template(
            "profile.html",
            user=user,
            bmi=bmi,
            bmi_category=bmi_category,
            bmr=bmr,
            tdee=tdee
        )


    except Exception as e:

        print("Profile error:", e)

        if db:

            db.rollback()

        flash(
            "Unable to process profile.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )


    finally:

        if cursor:

            cursor.close()

        if db:

            db.close()


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================================================
# AI NUTRITION INSIGHT
# =========================================================

def generate_nutrition_insight(food_name, nutrition, user):

    calories = float(nutrition.get("calories") or 0)
    protein = float(nutrition.get("protein") or 0)
    carbs = float(nutrition.get("carbohydrates") or 0)
    fat = float(nutrition.get("fat") or 0)
    fiber = float(nutrition.get("fiber") or 0)
    sodium = float(nutrition.get("sodium") or 0)

    goal = str(user.get("goal") or "").lower()

    messages = []
    recommendations = []

    if "lose" in goal and calories >= 500:
        messages.append("This meal is relatively high in calories.")
        recommendations.append(
            "Consider a lighter next meal and include vegetables."
        )

    if "gain" in goal and protein >= 20:
        messages.append("This meal provides a useful amount of protein.")
        recommendations.append(
            "This supports a muscle-gain focused diet."
        )

    if protein < 10:
        messages.append("Protein content is relatively low.")
        recommendations.append(
            "Consider adding eggs, dal, paneer, curd or another protein-rich food."
        )

    if carbs >= 50:
        messages.append("This meal is high in carbohydrates.")
        recommendations.append(
            "Balance the rest of the day with protein and vegetables."
        )

    if fat >= 20:
        messages.append("Fat content is relatively high.")
        recommendations.append(
            "Keep later meals moderate in added oils and fried foods."
        )

    if fiber < 5:
        messages.append("Fiber content is low.")
        recommendations.append(
            "Add vegetables, fruit, whole grains or legumes."
        )

    if sodium >= 600:
        messages.append("Sodium content is relatively high.")
        recommendations.append(
            "Choose lower-sodium foods for your next meal."
        )

    if not messages:
        messages.append(
            f"{food_name.title()} has a reasonably balanced nutrition profile."
        )

    if not recommendations:
        recommendations.append(
            "Continue balancing your meals across the day."
        )

    return {
        "message": " ".join(messages),
        "recommendation": " ".join(recommendations)
    }

# =========================================================
# FOOD ANALYSIS & SCANNER
# =========================================================

@app.route("/predict", methods=["POST"])
@app.route("/analyze", methods=["POST"])
@login_required
def analyze():

    db = None
    cursor = None

    try:

        # Check image in request
        if "food_image" not in request.files:
            return jsonify({
                "success": False,
                "error": "No image uploaded. Please choose a food photo."
            }), 400

        file = request.files["food_image"]

        if file.filename == "":
            return jsonify({
                "success": False,
                "error": "No image selected."
            }), 400

        if not allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": "Unsupported image format. Allowed formats: PNG, JPG, JPEG, WEBP."
            }), 400

        # Save image securely with unique filename
        import time
        orig_name = secure_filename(file.filename) or "capture.jpg"
        name_part, ext_part = os.path.splitext(orig_name)
        if not ext_part:
            ext_part = ".jpg"
        filename = f"{name_part}_{session['user_id']}_{int(time.time() * 1000)}{ext_part}"

        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)


        # AI Food Recognition
        result = recognize_food(path)
        food_name = result["food"]
        confidence = result["confidence"]
        is_demo = result.get("is_demo", False)
        demo_notice = result.get("demo_notice", "")

        # Connect to Database
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Retrieve Nutrition data (from MySQL food_items or reference foods)
        nutrition = get_nutrition_data(food_name, db_cursor=cursor, quantity=1.0)

        # Calculate explainable Health Score (0-100)
        health_score = calculate_health_score(nutrition)

        # Get User Profile for personalized advice
        cursor.execute(
            """
            SELECT age, height, weight, gender, activity_level, goal
            FROM users
            WHERE id = %s
            LIMIT 1
            """,
            (session["user_id"],)
        )
        user = cursor.fetchone() or {}

        # Generate AI insights & recommendations
        insight = generate_nutrition_insights(food_name, nutrition, user)

        # Save to meal_history
        food_id = nutrition.get("id")
        meal_type = request.form.get("meal_type") or "Meal"

        cursor.execute(
            """
            INSERT INTO meal_history
            (
                user_id,
                food_id,
                food_name,
                quantity,
                calories,
                protein,
                carbohydrates,
                fat,
                fiber,
                image_path,
                meal_type
            )
            VALUES
            (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """,
            (
                session["user_id"],
                food_id,
                food_name.title(),
                1.0,
                nutrition["calories"],
                nutrition["protein"],
                nutrition["carbohydrates"],
                nutrition["fat"],
                nutrition["fiber"],
                path,
                meal_type
            )
        )

        meal_id = cursor.lastrowid

        # Save AI insight to ai_analysis (storing health score inside ai_message for history reference)
        full_ai_message = f"[Health Score: {health_score['score']}/100 - {health_score['category']}] {insight['message']}"

        cursor.execute(
            """
            INSERT INTO ai_analysis
            (
                user_id,
                meal_id,
                ai_message,
                recommendation
            )
            VALUES
            (
                %s, %s, %s, %s
            )
            """,
            (
                session["user_id"],
                meal_id,
                full_ai_message,
                insight["recommendation"]
            )
        )

        db.commit()

        return jsonify({
            "success": True,
            "food": food_name.title(),
            "confidence": confidence,
            "nutrition": nutrition,
            "health_score": health_score,
            "ai_message": insight["message"],
            "recommendation": insight["recommendation"],
            "meal_saved": True,
            "meal_id": meal_id,
            "image_url": f"/uploads/{filename}",
            "is_demo": is_demo,
            "demo_notice": demo_notice
        })

    except Exception as e:
        print("Food analysis error:", e)
        if db:
            try:
                db.rollback()
            except Exception:
                pass

        return jsonify({
            "success": False,
            "error": f"Food analysis failed: {str(e)}"
        }), 500

    finally:
        if cursor:
            try: cursor.close()
            except Exception: pass
        if db:
            try: db.close()
            except Exception: pass


# =========================================================
# SAVE MEAL (EXPLICIT SAVE / UPDATE)
# =========================================================

@app.route("/save-meal", methods=["POST"])
@login_required
def save_meal():
    db = None
    cursor = None
    try:
        data = request.get_json(silent=True) or request.form
        food_name = data.get("food_name", "Scanned Food")
        calories = float(data.get("calories", 0))
        protein = float(data.get("protein", 0))
        carbs = float(data.get("carbohydrates", 0))
        fat = float(data.get("fat", 0))
        fiber = float(data.get("fiber", 0))
        quantity = float(data.get("quantity", 1.0))
        meal_type = data.get("meal_type", "Meal")
        image_path = data.get("image_path", "")
        ai_message = data.get("ai_message", "")
        recommendation = data.get("recommendation", "")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            INSERT INTO meal_history
            (user_id, food_name, quantity, calories, protein, carbohydrates, fat, fiber, image_path, meal_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session["user_id"],
                food_name,
                quantity,
                calories,
                protein,
                carbs,
                fat,
                fiber,
                image_path,
                meal_type
            )
        )
        meal_id = cursor.lastrowid

        if ai_message or recommendation:
            cursor.execute(
                """
                INSERT INTO ai_analysis (user_id, meal_id, ai_message, recommendation)
                VALUES (%s, %s, %s, %s)
                """,
                (session["user_id"], meal_id, ai_message, recommendation)
            )

        db.commit()
        return jsonify({"success": True, "meal_id": meal_id, "message": "Meal saved successfully!"})

    except Exception as e:
        print("Save meal error:", e)
        if db:
            try: db.rollback()
            except Exception: pass
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        if cursor:
            try: cursor.close()
            except Exception: pass
        if db:
            try: db.close()
            except Exception: pass


# =========================================================
# ANALYTICS
# =========================================================

@app.route("/analytics")
@login_required
def analytics():
    db = None
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        # 1. Total meals logged and overall nutrition totals
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_meals,
                COALESCE(SUM(calories), 0) AS total_calories,
                COALESCE(SUM(protein), 0) AS total_protein,
                COALESCE(SUM(carbohydrates), 0) AS total_carbs,
                COALESCE(SUM(fat), 0) AS total_fat,
                COALESCE(SUM(fiber), 0) AS total_fiber,
                COALESCE(AVG(calories), 0) AS avg_calories
            FROM meal_history
            WHERE user_id = %s
            """,
            (session["user_id"],)
        )
        overall = cursor.fetchone() or {}

        # 2. Daily calories & macros for last 7 days with meals
        cursor.execute(
            """
            SELECT
                DATE(created_at) AS meal_date,
                COUNT(*) AS meals_count,
                ROUND(SUM(calories), 1) AS daily_calories,
                ROUND(SUM(protein), 1) AS daily_protein,
                ROUND(SUM(carbohydrates), 1) AS daily_carbs,
                ROUND(SUM(fat), 1) AS daily_fat,
                ROUND(SUM(fiber), 1) AS daily_fiber
            FROM meal_history
            WHERE user_id = %s
            GROUP BY DATE(created_at)
            ORDER BY meal_date DESC
            LIMIT 7
            """,
            (session["user_id"],)
        )
        daily_trends = cursor.fetchall() or []
        daily_trends.reverse()  # Chronological order for charts

        # 3. Meal frequency by type
        cursor.execute(
            """
            SELECT
                COALESCE(meal_type, 'Meal') AS meal_type,
                COUNT(*) AS count
            FROM meal_history
            WHERE user_id = %s
            GROUP BY meal_type
            ORDER BY count DESC
            """,
            (session["user_id"],)
        )
        meal_types = cursor.fetchall() or []

        # 4. Calculate average health score across user meals
        cursor.execute(
            """
            SELECT calories, protein, carbohydrates, fat, fiber
            FROM meal_history
            WHERE user_id = %s
            """,
            (session["user_id"],)
        )
        all_meals = cursor.fetchall() or []
        if all_meals:
            scores = [calculate_health_score(m)["score"] for m in all_meals]
            avg_health_score = round(sum(scores) / len(scores))
        else:
            avg_health_score = 0

        return render_template(
            "analytics.html",
            user_name=session.get("user_name"),
            overall=overall,
            daily_trends=daily_trends,
            meal_types=meal_types,
            avg_health_score=avg_health_score
        )

    except Exception as e:
        print("Analytics error:", e)
        return render_template(
            "analytics.html",
            user_name=session.get("user_name"),
            overall={"total_meals": 0, "total_calories": 0, "total_protein": 0, "total_carbs": 0, "total_fat": 0, "total_fiber": 0, "avg_calories": 0},
            daily_trends=[],
            meal_types=[],
            avg_health_score=0
        )

    finally:
        if cursor:
            try: cursor.close()
            except Exception: pass
        if db:
            try: db.close()
            except Exception: pass


# =========================================================
# CHATBOT & API CHAT
# =========================================================

@app.route("/chatbot")
@login_required
def chatbot_page():
    return render_template("chatbot.html", user_name=session.get("user_name"))


@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    db = None
    cursor = None
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get("message", "")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT name, age, height, weight, gender, activity_level, goal
            FROM users
            WHERE id = %s
            LIMIT 1
            """,
            (session["user_id"],)
        )
        user = cursor.fetchone() or {}

        reply = handle_chat_message(
            user_message=user_message,
            user_id=session["user_id"],
            cursor=cursor,
            user_profile=user
        )

        return jsonify({
            "success": True,
            "reply": reply
        })

    except Exception as e:
        print("Chatbot API error:", e)
        return jsonify({
            "success": False,
            "reply": f"Sorry, I encountered an error answering that: {str(e)}"
        }), 500

    finally:
        if cursor:
            try: cursor.close()
            except Exception: pass
        if db:
            try: db.close()
            except Exception: pass



# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )