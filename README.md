# 🚀 Gravity — Age & Gender Detector

> **AI-powered age and gender detection from webcam or uploaded images, driven by Mistral AI's Pixtral Large vision model.**

---

## 📌 Overview

**Gravity** is a lightweight, real-time web application that estimates a person's **age range**, **gender**, and **confidence score** by analyzing face images. It uses the state-of-the-art **Pixtral Large** multimodal vision model from Mistral AI (accessed via OpenRouter) as its AI backbone — no traditional CV models, no local GPU required.

The app runs as a local Flask server that acts as a **secure proxy** between the browser and the Mistral API. Your API key is never exposed to the browser.

---

## 🎯 Use Cases

| Use Case | Description |
|---|---|
| 🧪 **Research & Demos** | Quickly demo AI vision capabilities without deploying cloud infrastructure |
| 📊 **Audience Analytics** | Estimate demographic information from images (retail, events, etc.) |
| 🎮 **Interactive Prototypes** | Integrate into kiosks, games, or creative installations |
| 🛡️ **Age Verification Assistance** | Aid manual age verification workflows |
| 🤖 **AI Learning Tool** | Study multimodal LLM usage and vision API integration |

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.9+** | Core runtime |
| **Flask** | Lightweight web server & REST API |
| **Flask-CORS** | Enable cross-origin requests from the browser |
| **python-dotenv** | Load environment variables from `.env` |
| **Requests** | HTTP client for calling the Mistral/OpenRouter API |

### Frontend
| Technology | Purpose |
|---|---|
| **HTML5 / Vanilla JS** | UI structure and logic |
| **TailwindCSS (CDN)** | Utility-first styling |
| **WebRTC (`getUserMedia`)** | Live webcam access |
| **Canvas API** | Capture frames from the webcam video stream |
| **Fetch API** | Send images to the local Flask server |

### AI / API
| Technology | Purpose |
|---|---|
| **Mistral AI — Pixtral Large** | Multimodal vision LLM for age & gender inference |
| **OpenRouter** | API gateway used to access the Pixtral Large model |

---

## 📁 Project Structure

```
Age_Gender_Detector/
├── server.py          # Flask backend — API proxy & routing
├── index.html         # Single-page frontend (served by Flask)
├── requirements.txt   # Python dependencies
├── .env               # API key configuration (not committed to git)
└── .gitignore         # Git ignore rules
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python **3.9** or higher
- `pip` package manager
- An **OpenRouter API key** (free tier available)
  - Sign up at [https://openrouter.ai/keys](https://openrouter.ai/keys)

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/<your-username>/Age_Gender_Detector.git
cd Age_Gender_Detector
```

---

### Step 2 — Create a Virtual Environment (Recommended)

**Using `venv`:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**Or using Conda:**
```bash
conda create -n age_gender python=3.10 -y
conda activate age_gender
```

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `flask`
- `flask-cors`
- `python-dotenv`
- `requests`

---

### Step 4 — Configure the API Key

Create a `.env` file in the project root (copy from the example below):

```bash
# .env
MISTRAL_API_KEY=your_openrouter_api_key_here
```

> ⚠️ **Never commit your `.env` file.** It is already listed in `.gitignore`.

To get your key:
1. Go to [https://openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up or log in
3. Generate a new API key
4. Paste it into the `.env` file

---

### Step 5 — Run the Server

```bash
python server.py
```

Expected output:

```
✅ Mistral API key loaded (sk-or-v1...)
🚀 Server running at http://localhost:5000
```

---

### Step 6 — Open the App

Open your browser and navigate to:

```
http://localhost:5000
```

---

## 🖥️ How to Use

### 📷 Webcam Mode
1. Click **▶️ Start Camera** to activate your webcam.
2. Click **📸 Analyze Now** (or press `SPACE`) to analyze the current frame.
3. The app auto-analyzes every **5 seconds** while the camera is running.

### 🖼️ Image Upload Mode
1. Switch to the **Upload Image** tab.
2. Drag & drop an image or click **📁 Choose File**.
3. Click **🔍 Analyze Image** to submit.

### 📊 Results
The results panel shows:
- **Estimated Age** — returned as a range (e.g., `25-30`)
- **Gender** — `Male`, `Female`, or `Non-binary`
- **Confidence Score** — displayed as a percentage progress bar

---

## 🔒 Privacy & Security

- Images are sent only to your **local Flask server**.
- The Flask server securely forwards the image to the Mistral API.
- Your **API key is stored server-side** in `.env` and is never sent to the browser.
- No images or results are stored or logged by default.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the frontend (`index.html`) |
| `POST` | `/analyze` | Accepts a base64-encoded JPEG from the webcam |
| `POST` | `/analyze-file` | Accepts a multipart image file upload |

### `/analyze` Request Body
```json
{
  "image": "<base64-encoded JPEG string>"
}
```

### `/analyze-file` Request Body
`multipart/form-data` with a field named `file`.

### Response (both endpoints)
```json
{
  "age": "25-30",
  "gender": "Male",
  "confidence": 0.92
}
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| `MISTRAL_API_KEY is not set` | Check `.env` file exists and contains a valid key |
| Camera not starting | Ensure browser has webcam permission; use `http://localhost` (not IP) |
| `Mistral API timed out` | Check your internet connection; retry |
| `HTTP 401 Unauthorized` | Your API key is invalid or expired; generate a new one |
| `Could not extract JSON from reply` | The model failed to parse the face; try a clearer image |

---

## 📄 License

This project is open-source. Feel free to fork, modify, and use it in your own projects.

---

## 🙌 Acknowledgements

- [Mistral AI](https://mistral.ai/) — Pixtral Large vision model
- [OpenRouter](https://openrouter.ai/) — API gateway
- [Flask](https://flask.palletsprojects.com/) — Python web framework
- [TailwindCSS](https://tailwindcss.com/) — CSS framework
