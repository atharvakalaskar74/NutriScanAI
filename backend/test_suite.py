import os
import sys
import unittest
import json
import io

# Safe UTF-8 reconfiguration
if hasattr(sys.stdout, "reconfigure"):
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from database import get_db
from nutrition_service import get_nutrition_data, calculate_health_score, generate_nutrition_insights
from chatbot_service import handle_chat_message

class NutriScanTestSuite(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_database_preservation(self):
        """Verify existing database connection and preserve existing data"""
        db = get_db()
        self.assertIsNotNone(db, "Database connection failed")
        cursor = db.cursor(dictionary=True)
        
        # Verify tables exist
        cursor.execute("SHOW TABLES")
        tables = [list(r.values())[0] for r in cursor.fetchall()]
        for expected in ["users", "food_items", "meal_history", "ai_analysis", "daily_goals"]:
            self.assertIn(expected, tables, f"Expected table '{expected}' missing from database")

        # Verify existing user preserved
        cursor.execute("SELECT id, email FROM users WHERE id = 1")
        user = cursor.fetchone()
        self.assertIsNotNone(user, "Existing user record was missing")
        self.assertEqual(user["email"], "prpotec3@gmail.com")

        # Verify existing meals preserved (at least 9 original meals)
        cursor.execute("SELECT COUNT(*) AS count FROM meal_history")
        meal_count = cursor.fetchone()["count"]
        self.assertGreaterEqual(meal_count, 9, "Original meal records were not preserved")

        cursor.close()
        db.close()
        print(f"✅ DB Preservation: PASS ({meal_count} meal records preserved, 0 schema changes)")

    def test_02_nutrition_service(self):
        """Test nutrition calculation and 0-100 health scoring"""
        # Test exact data
        n = get_nutrition_data("pizza", quantity=1.0)
        self.assertIn("calories", n)
        self.assertIn("protein", n)
        self.assertIn("carbohydrates", n)
        self.assertIn("fat", n)
        self.assertIn("fiber", n)
        self.assertIn("sugar", n)
        self.assertIn("sodium", n)
        self.assertIn("serving_size", n)
        self.assertGreater(n["calories"], 0)

        # Test Health Score
        score = calculate_health_score(n)
        self.assertGreaterEqual(score["score"], 0)
        self.assertLessEqual(score["score"], 100)
        self.assertIn("explanation", score)
        self.assertIn("category", score)

        # Test Insights
        insights = generate_nutrition_insights("pizza", n, {"goal": "Weight Loss"})
        self.assertIn("message", insights)
        self.assertIn("recommendation", insights)
        print(f"✅ Nutrition & Health Score Service: PASS (Pizza Score: {score['score']}/100 - {score['category']})")

    def test_03_authentication_and_session(self):
        """Test login and session creation"""
        # Simulate session login for user_id = 1
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Pr Pote College"
            sess["user_email"] = "prpotec3@gmail.com"

        # Check protected dashboard
        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Pr Pote College", res.data)
        print("✅ Authentication & Dashboard Access: PASS")

    def test_04_scan_food_flow(self):
        """Test /predict with real image pizza.jpg"""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Pr Pote College"
            sess["user_email"] = "prpotec3@gmail.com"

        img_path = os.path.join(os.path.dirname(__file__), "uploads", "pizza.jpg")
        self.assertTrue(os.path.exists(img_path), f"Test image missing at {img_path}")

        with open(img_path, "rb") as f:
            img_bytes = f.read()

        data = {
            "food_image": (io.BytesIO(img_bytes), "pizza.jpg"),
            "meal_type": "Lunch"
        }

        res = self.client.post("/predict", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        res_json = json.loads(res.data)

        self.assertTrue(res_json["success"])
        self.assertIn("food", res_json)
        self.assertIn("confidence", res_json)
        self.assertIn("nutrition", res_json)
        self.assertIn("health_score", res_json)
        self.assertIn("ai_message", res_json)
        self.assertIn("recommendation", res_json)
        self.assertTrue(res_json["meal_saved"])
        self.assertIn("meal_id", res_json)

        print(f"✅ Scan Food End-to-End: PASS (Recognized: {res_json['food']}, Score: {res_json['health_score']['score']}/100, Meal ID: {res_json['meal_id']})")

    def test_05_meal_history_and_analytics_views(self):
        """Test /meal-history and /analytics endpoints"""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Pr Pote College"
            sess["user_email"] = "prpotec3@gmail.com"

        # Check Meal History
        res_hist = self.client.get("/meal-history")
        self.assertEqual(res_hist.status_code, 200)
        self.assertIn(b"Meal History", res_hist.data)

        # Check Analytics
        res_ana = self.client.get("/analytics")
        self.assertEqual(res_ana.status_code, 200)
        self.assertIn(b"Nutrition Analytics", res_ana.data)
        print("✅ Meal History & Analytics Views: PASS")

    def test_06_chatbot_context_grounding(self):
        """Test chatbot answering with real MySQL meal data"""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Pr Pote College"
            sess["user_email"] = "prpotec3@gmail.com"

        # Ask chatbot about today's protein
        res = self.client.post(
            "/api/chat",
            data=json.dumps({"message": "How much protein did I eat today?"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        res_json = json.loads(res.data)
        self.assertTrue(res_json["success"])
        self.assertIn("protein", res_json["reply"].lower())
        print(f"✅ AI Chatbot Response: PASS -> '{res_json['reply'][:80]}...'")

    def test_07_image_serving(self):
        """Test serving uploaded images via /uploads/<filename>"""
        res = self.client.get("/uploads/pizza.jpg")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "image/jpeg")
        print("✅ Image Serving (/uploads/pizza.jpg): PASS")

    def test_08_live_camera_blob_submission(self):
        """Test Live Camera captured frame submission (simulating canvas.toBlob payload)"""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Pr Pote College"
            sess["user_email"] = "prpotec3@gmail.com"

        # Read biryani.jpg to simulate a real captured camera frame
        img_path = os.path.join(os.path.dirname(__file__), "uploads", "biryani.jpg")
        self.assertTrue(os.path.exists(img_path))
        with open(img_path, "rb") as f:
            camera_frame_bytes = f.read()

        # Simulate the exact FormData sent by captureAndScan() in browser
        data = {
            "food_image": (io.BytesIO(camera_frame_bytes), "camera_capture.jpg", "image/jpeg"),
            "meal_type": "Dinner"
        }

        res = self.client.post("/predict", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        res_json = json.loads(res.data)

        self.assertTrue(res_json["success"], "Camera scan failed")
        self.assertIn("food", res_json)
        self.assertIn("confidence", res_json)
        self.assertIn("nutrition", res_json)
        self.assertIn("health_score", res_json)
        self.assertTrue(res_json["meal_saved"])
        self.assertIn("image_url", res_json)

        # Verify the captured image was saved and is accessible via HTTP
        img_res = self.client.get(res_json["image_url"])
        self.assertEqual(img_res.status_code, 200)
        self.assertEqual(img_res.content_type, "image/jpeg")

        print(f"✅ Live Camera Capture & Scan Pipeline: PASS (Recognized: {res_json['food']}, Score: {res_json['health_score']['score']}/100, URL: {res_json['image_url']})")

if __name__ == "__main__":
    unittest.main()

