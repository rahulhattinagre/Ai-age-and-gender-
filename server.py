import os
import re
import json
import base64
import requests
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv
from functools import wraps

load_dotenv()
print("DEBUG KEY:", os.getenv("MISTRAL_API_KEY"))

app = Flask(__name__, static_folder="static", static_url_path="/static", template_folder="templates")
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key-2024")

# MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["age_gender_db"]
users_collection = db["users"]
users_collection.create_index("email", unique=True)
print("✅ MongoDB:", db.name, users_collection.name)

# AI
MISTRAL_URL = "https://openrouter.ai/api/v1/chat/completions"
PROMPT = 'You are precise age/gender estimator. Main face only. STRICT JSON: {"age": "25-30", "gender": "Male", "confidence": 0.92}. Gender: "Male"/"Female"/"Non-binary".'

def get_api_key():
    key = os.getenv("MISTRAL_API_KEY", "").strip()
    print(f"DEBUG: API Key prefix: {'✅' if key else '❌'} {key[:10]}...")

    if not key or key.startswith("your_mistral"):
        return None, "MISTRAL_API_KEY missing/invalid in .env. Get at https://openrouter.ai/keys"

    return key, None

def call_mistral(image_b64: str, mime_type: str = "image/jpeg", retries: int = 3):
    models = [
        "mistralai/pixtral-large-2411",
        "mistralai/pixtral-12b-2409"  # Cheaper fallback
    ]
    
    key, err = get_api_key()
    if err: return None, err
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Age Gender AI Detector",
        "User-Agent": "AgeGenderAI/1.0"
    }
    
    for attempt in range(retries):
        for model in models:
            try:
                print(f"🔄 AI attempt {attempt+1}/{retries}, model: {model}")
                payload = {
                    "model": model,
                    "temperature": 0.1,
                    "max_tokens": 150,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": PROMPT},
                            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}}
                        ]
                    }]
                }
                
                resp = requests.post(MISTRAL_URL, json=payload, headers=headers, timeout=30)
                print(f"📡 Status: {resp.status_code}")
                
                if resp.status_code == 402:
                    try:
                        error_data = resp.json().get('error', {})
                        msg = error_data.get('message', 'Payment required (low credits/quota)')
                        return None, f"🚫 402 QUOTA: {msg}. Add credits at https://openrouter.ai/billing or try free model."
                    except:
                        return None, "🚫 402 QUOTA: Low credits. Add at openrouter.ai/billing"
                
                if resp.status_code == 429:
                    wait_sec = int(resp.headers.get('retry-after', 5))
                    return None, f"⏳ Rate limit (429). Wait {wait_sec}s. Limits: {dict(resp.headers)}"
                
                if not resp.ok:
                    try:
                        error_data = resp.json().get('error', {})
                        msg = error_data.get('message', f"HTTP {resp.status_code}")
                        return None, f"API ({resp.status_code}): {msg}"
                    except:
                        return None, f"API {resp.status_code}"
                
                data = resp.json()
                raw = data["choices"][0]["message"]["content"]
                match = re.search(r"\{[\s\S]*?}", raw)
                if match:
                    result = json.loads(match.group())
                    print("✅ AI Success:", result)
                    return result, None
                else:
                    print("⚠️ No JSON:", raw[:100])
                    continue
                
            except requests.exceptions.Timeout:
                print("⏰ Timeout")
                continue
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
        
        if attempt < retries - 1:
            time.sleep(2 ** attempt)
    
    return None, "Failed retries. Check credits/limits at openrouter.ai"

# Helpers
def is_logged_in():
    return "user_email" in session

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

def get_user(email):
    return users_collection.find_one({"email": email})

# DevTools fix
@app.route("/.well-known/appspecific/com.chrome.devtools.json")
def devtools():
    return jsonify({})

# Test API key
@app.route("/test-key", methods=["GET"])
def test_key():
    key, err = get_api_key()
    if err:
        return jsonify({"valid": False, "error": err}), 400
    
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    try:
        resp = requests.get("https://openrouter.ai/api/v1/meta/models", headers=headers, timeout=10)
        if resp.status_code == 200:
            return jsonify({"valid": True, "status": "OK", "models_available": len(resp.json()['data'])})
        elif resp.status_code == 402:
            return jsonify({"valid": False, "error": "402 - No credits/quota", "fix": "https://openrouter.ai/billing"}), 402
        else:
            return jsonify({"valid": False, "error": f"API {resp.status_code}"}), resp.status_code
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

# Routes
@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html") if not is_logged_in() else redirect("/dashboard")

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"].lower().strip()
    password = request.form["password"]
    user = get_user(email)
    if user and check_password_hash(user["password"], password):
        session["user_email"] = email
        session["user_name"] = user["name"]
        return redirect("/dashboard")
    return render_template("login.html", error="Invalid email/password")

@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html") if not is_logged_in() else redirect("/dashboard")

@app.route("/signup", methods=["POST"])
def signup_post():
    name = request.form["name"].strip()
    email = request.form["email"].lower().strip()
    password = request.form["password"]
    if len(password) < 4:
        return render_template("signup.html", error="Password must be at least 4 characters")
    if users_collection.find_one({"email": email}):
        return render_template("signup.html", error="Email already registered. Please login or use a different email.")
    hashed = generate_password_hash(password)
    users_collection.insert_one({"name": name, "email": email, "password": hashed})
    session["user_email"] = email
    session["user_name"] = name
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/dashboard")
@login_required
def dashboard():
    user = get_user(session["user_email"])
    user_name = user["name"] if user else session.get("user_name", "User")
    return render_template("index.html", user_name=user_name)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    result, err = call_mistral(data["image"])
    return jsonify(result or {"error": err})

@app.route("/analyze-file", methods=["POST"])
def analyze_file():
    file = request.files["file"]
    b64 = base64.b64encode(file.read()).decode()
    result, err = call_mistral(b64, file.mimetype or "image/jpeg")
    return jsonify(result or {"error": err})

if __name__ == "__main__":
    print("🚀 FIXED server.py - 402/Rate Limit Handling + Fallbacks + /test-key - localhost:5000")
    print("💡 Test quota: powershell 'Invoke-WebRequest -Uri http://localhost:5000/test-key | Select -ExpandProperty Content'")
    app.run(debug=True, port=5000)
