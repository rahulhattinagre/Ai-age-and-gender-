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

# MongoDB globals
client = None
users_collection = {}
db_name = "in-memory"

try:
    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri:
        print(f"DEBUG MONGO_URI: {'mongodb+srv://***:' if 'mongodb+srv' in mongo_uri else mongo_uri[:40]}...{mongo_uri[-25:] if len(mongo_uri) > 50 else ''}")
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        db = client["age_gender_db"]
        users_collection = db["users"]
        users_collection.create_index("email", unique=True)
        db_name = db.name
        print("✅ MongoDB Connected:", db_name)
    else:
        print("⚠️ No MONGO_URI in .env")
except Exception as e:
    print(f"⚠️ MongoDB Error: {str(e)[:100]}. Using in-memory users DB (no persistence).")
    client = None
    users_collection = {}
    db_name = "in-memory"

print(f"DB Mode: {db_name}, Type: {'MongoDB' if client else 'Dict'}")

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
        "mistralai/pixtral-12b-2409"
    ]
    
    key, err = get_api_key()
    if err: return None, err
    
    headers = {
        "Authorization": f"Bear er {key}",
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
                        msg = error_data.get('message', 'Payment required')
                        return None, f"🚫 402 QUOTA: {msg}. Add credits at https://openrouter.ai/billing"
                    except:
                        return None, "🚫 402 QUOTA: Low credits."
                
                if resp.status_code == 429:
                    wait_sec = int(resp.headers.get('retry-after', 5))
                    return None, f"⏳ Rate limit. Wait {wait_sec}s."
                
                if not resp.ok:
                    try:
                        error_data = resp.json().get('error', {})
                        msg = error_data.get('message', f"HTTP {resp.status_code}")
                        return None, f"API ({resp.status_code}): {msg}"
                    except:
                        return None, f"API {resp.status_code}"
                
                data = resp.json()
                raw = data["choices"][0]["message"]["content"]
                match = re.search(r"\{[\\s\\S]*?}", raw)
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
    
    return None, "Failed retries. Check credits at openrouter.ai"

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
    if client is None:
        return users_collection.get(email.lower().strip())
    return users_collection.find_one({"email": email})

@app.route("/.well-known/appspecific/com.chrome.devtools.json")
def devtools():
    return jsonify({})

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
            return jsonify({"valid": False, "error": "402 - No credits", "fix": "https://openrouter.ai/billing"}), 402
        else:
            return jsonify({"valid": False, "error": f"API {resp.status_code}"}), resp.status_code
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

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
    if get_user(email):
        return render_template("signup.html", error="Email already registered. Please login or use a different email.")
    hashed = generate_password_hash(password)
    user_doc = {"name": name, "email": email, "password": hashed}
    if client is None:
        users_collection[email] = user_doc
    else:
        users_collection.insert_one(user_doc)
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
    user_name = user["name"] if user and "name" in user else session.get("user_name", "User")
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
    print("🚀 Age Gender Detection Server - MongoDB Fallback Enabled")
    print(" - http://localhost:5000")
    print(" - Test API quota: http://localhost:5000/test-key")
    print(" - Fix Atlas: Whitelist IP 0.0.0.0/0, check MONGO_URI format")
    app.run(debug=True, port=5000)
