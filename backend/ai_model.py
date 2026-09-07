import os
import sys

# Ensure UTF-8 stdout/stderr on Windows consoles to prevent UnicodeEncodeError with emojis
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

FOODS = [
    "chicken biryani",
    "vegetable biryani",
    "mutton biryani",
    "fried rice",
    "pulao",
    "butter chicken",
    "chicken curry",
    "dal",
    "paneer tikka",
    "palak paneer",
    "samosa",
    "dosa",
    "idli",
    "poha",
    "upma",
    "chapati",
    "dal rice",
    "vada pav",
    "pav bhaji",
    "rajma rice",
    "pizza",
    "burger",
    "noodles",
    "pasta",
    "salad",
    "sandwich",
    "omelette",
    "chole bhature"
]

classifier = None
_model_error = None

def get_classifier():
    global classifier, _model_error
    if classifier is None and _model_error is None:
        try:
            from transformers import pipeline
            print("🤖 Loading NutriScan AI food model (openai/clip-vit-base-patch32)...")
            classifier = pipeline(
                "zero-shot-image-classification",
                model="openai/clip-vit-base-patch32"
            )
            print("✅ NutriScan AI model loaded successfully!")
        except Exception as e:
            _model_error = str(e)
            print(f"⚠️ Warning: NutriScan AI model load failed: {e}")
    return classifier


def recognize_food(image_path):
    clf = get_classifier()
    if clf is not None:
        try:
            results = clf(image_path, candidate_labels=FOODS)
            best = results[0]
            return {
                "food": best["label"],
                "confidence": round(best["score"] * 100, 2),
                "is_demo": False,
                "alternatives": [
                    {"food": r["label"], "confidence": round(r["score"] * 100, 2)}
                    for r in results[1:4]
                ]
            }
        except Exception as e:
            print(f"Inference error with CLIP model: {e}")

    # Fallback / Demo Mode if AI model cannot run or failed
    filename = os.path.basename(image_path).lower()
    fallback_food = "pizza"
    for candidate in FOODS:
        if candidate.replace(" ", "") in filename or any(w in filename for w in candidate.split()):
            fallback_food = candidate
            break

    return {
        "food": fallback_food,
        "confidence": 85.0,
        "is_demo": True,
        "demo_notice": "DEMO MODE — AI SERVICE UNAVAILABLE",
        "alternatives": []
    }