# 🥗 NutriScan AI — AI-Powered Food Nutrition & Health Intelligence

NutriScan AI is a full-stack nutritional tracking and analysis web application. It combines deep learning computer vision (HuggingFace CLIP zero-shot classification) with an explainable nutritional intelligence engine, goal-oriented AI recommendations, interactive MySQL data tracking, and a context-aware nutrition chatbot.

---

## 🌟 Features

- **📸 Instant AI Food Scanner**: Upload or capture any meal photo to immediately recognize foods with confidence scoring.
- **📊 Complete Nutritional Profiling**: Computes exact calories, protein, carbohydrates, fat, dietary fiber, sugar, sodium, and serving sizes.
- **⭐ 0–100 Explainable Health Score**: Evaluates nutritional density, fiber content, protein ratio, sodium, and sugar with a clear rationale.
- **🤖 Goal-Tailored AI Recommendations**: Delivers actionable advice tailored to your fitness objective (*Weight Loss*, *Muscle Gain*, or *Maintenance*).
- **📅 Real-Time Meal History**: Persistent meal logging with photos, timestamps, macros, and AI recommendations stored in MySQL.
- **📊 Interactive Dashboard**: Tracks today's calorie and macro intake against personalized targets calculated from BMR and TDEE equations.
- **📈 Advanced Analytics**: Visualizes weekly calorie intake, macronutrient distribution, and health trends using Chart.js.
- **💬 Context-Aware AI Chatbot**: Inquires into your actual database records (*"How much protein did I eat today?"*, *"What were my calories today?"*) or offers general dietary advice.
- **🔐 Secure Authentication & Profile**: Password hashing with Werkzeug, session protection, and personalized biometric configuration.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Flask 3.1, Werkzeug
- **AI & Computer Vision**: PyTorch, HuggingFace Transformers (`openai/clip-vit-base-patch32` zero-shot image classification)
- **Database**: MySQL (`nutriscan` database connected via `mysql-connector-python`)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Chart.js, Jinja2 Templates

---

## 📁 Project Structure

```text
NutriScanAI_Original/
├── backend/
│   ├── app.py                   # Main Flask application and API routes
│   ├── database.py              # MySQL connection manager
│   ├── ai_model.py              # CLIP zero-shot vision classification
│   ├── nutrition_service.py     # Nutrition calculation, 0-100 health scoring, AI insights
│   ├── chatbot_service.py       # Context-aware chatbot with MySQL grounding
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── login.html           # Authentication login
│   │   ├── register.html        # User registration
│   │   ├── dashboard.html       # Primary user dashboard
│   │   ├── index.html           # AI Food scanner interface
│   │   ├── meal_history.html    # Saved meal history
│   │   ├── analytics.html       # Analytics & nutrition trends
│   │   ├── chatbot.html         # AI nutrition assistant
│   │   └── profile.html         # User biometrics & calorie goals
│   └── uploads/                 # Storage for scanned meal photos
├── requirements.txt             # Python package dependencies
├── .env.example                 # Environment configuration template
└── README.md                    # Project documentation
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- MySQL Server (e.g. via XAMPP, WAMP, or standalone MySQL on port 3306)

### 2. Database Configuration
Ensure MySQL is running on `localhost:3306`. The existing database name is `nutriscan`.
Connection settings are located in `backend/database.py`:
```python
host="localhost",
user="root",
password="",
database="nutriscan",
port=3306
```

### 3. Virtual Environment & Dependencies
Activate the virtual environment and install the pinned dependencies:
```powershell
# Windows
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🏃‍♂️ Running the Application

Start the Flask server from the `backend/` directory:
```powershell
cd d:\NutriScanAI_Original\backend
..\venv\Scripts\python.exe app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🔍 How Food Scanning Works (Dual Scanning Options)

NutriScan AI supports two scanning workflows that both feed into the identical deep-learning AI pipeline:

### Option 1: 📷 Live Camera Scanner
1. Navigate to `/scan-food` and select **Live Camera**.
2. Click **Open Camera** (native browser `navigator.mediaDevices.getUserMedia`).
3. Frame the meal inside the interactive viewfinder overlay.
4. (Optional) Use **Flip Camera** on mobile devices to switch between rear and front cameras.
5. Click **Capture & Scan**: Captures the exact video frame via HTML5 Canvas, exports to a high-fidelity JPEG Blob, and sends it to `/predict`.

### Option 2: 🖼️ Image Upload Scanner
1. Navigate to `/scan-food` and select **Upload Image**.
2. Choose a food photo (`.jpg`, `.jpeg`, `.png`, `.webp`) from your device files.
3. Review the instant preview and click **Scan Food**.

### Unified AI Processing Pipeline
```text
  [Live Camera Frame (Blob)] OR [Uploaded Image File]
                        ↓
            POST /predict (Flask backend)
                        ↓
       HuggingFace CLIP Vision Classifier (ai_model.py)
                        ↓
         Food Identified with AI Confidence %
                        ↓
   Nutrition Service: Calories, Protein, Carbs, Fat, Fiber,
            Sugar, Sodium & Serving Size
                        ↓
      0–100 Explainable Health Score Calculated
                        ↓
      Personalized AI Recommendations Generated
                        ↓
   Persistent Save to MySQL (meal_history & ai_analysis)
                        ↓
 UI Displays Complete Results, Health Score, Macros & Advice
```

> **🔒 Camera Security Note**:
> Browser camera access via `getUserMedia()` strictly requires a **Secure Context** (`https://` or `http://localhost` / `http://127.0.0.1`). When hosting on a local network or public IP, ensure HTTPS or an SSL reverse proxy (such as Nginx or Caddy) is configured for live camera permissions.


---

## 🧪 Testing Instructions

1. **Test Authentication**:
   - Register a new account or log in with existing user (`prpotec3@gmail.com`).
2. **Test Scanner Flow**:
   - Navigate to `/scan-food`, select an image (e.g. `backend/uploads/pizza.jpg`), choose meal type, and click **Scan Food**.
   - Verify that confidence %, calories, protein, carbs, fat, fiber, sugar, sodium, 0-100 health score, and AI recommendations are displayed.
3. **Verify Database Records**:
   - Open `/meal-history` and verify the scanned meal appears with its photo thumbnail and health score badge.
4. **Verify Dashboard & Analytics**:
   - Open `/dashboard` and check that today's calories, progress bars, and recent meals reflect the newly logged meal.
   - Open `/analytics` to inspect the weekly calorie and macronutrient charts.
5. **Verify AI Chatbot**:
   - Open `/chatbot` and ask: *"How much protein did I eat today?"*. Confirm it returns your authentic database numbers.
