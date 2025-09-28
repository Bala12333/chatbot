# 🌾 Crop Crystalline Chatbot - Complete Backend Setup Guide

## 📁 **Required Backend Files Structure**

```
crop_chatbot/                          # Django Project Root
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── .env                              # Environment variables
├── .env.example                      # Environment template
├── db.sqlite3                        # SQLite database (auto-generated)
│
├── crop_chatbot/                     # Django project settings
│   ├── __init__.py
│   ├── settings.py                   # Main Django settings
│   ├── urls.py                       # Main URL routing
│   ├── wsgi.py                       # WSGI configuration
│   └── asgi.py                       # ASGI configuration
│
├── chatbot/                          # Main chatbot app
│   ├── __init__.py
│   ├── admin.py                      # Django admin configuration
│   ├── apps.py                       # App configuration
│   ├── models.py                     # Database models
│   ├── views.py                      # API endpoints
│   ├── urls.py                       # App URL routing
│   ├── services.py                   # Core AI services
│   ├── tests.py                      # Unit tests
│   │
│   ├── migrations/                   # Database migrations
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   │
│   └── management/                   # Django management commands
│       ├── __init__.py
│       └── commands/
│           ├── __init__.py
│           ├── populate_knowledge_base.py
│           └── add_crop_knowledge.py
│
├── credentials/                      # Google Cloud credentials
│   └── google-cloud-key.json        # Service account key
│
└── media/                           # User uploads (audio files)
    └── audio/                       # Voice recordings
```

## 🔧 **1. Core Backend Files**

### **A. Dependencies (requirements.txt)**
```txt
Django>=4.2.0
google-cloud-speech>=2.20.0
google-cloud-texttospeech>=2.14.0
google-cloud-dialogflow>=2.20.0
google-generativeai>=0.3.0
python-dotenv>=1.0.0
requests>=2.31.0
django-cors-headers>=4.0.0
```

### **B. Environment Configuration (.env)**
```env
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Google Cloud credentials
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-cloud-key.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id

# Dialogflow settings
DIALOGFLOW_PROJECT_ID=your-dialogflow-project-id
DIALOGFLOW_LANGUAGE_CODE=en-US

# Gemini AI settings
GEMINI_API_KEY=your-gemini-api-key-here
```

## 🌐 **2. API Endpoints for Frontend Integration**

### **Available API Endpoints:**

#### **A. Text Chat API**
```
POST /api/chat/
Content-Type: application/json

Request:
{
    "message": "How to grow rice?",
    "session_id": "optional-session-id",
    "language_code": "auto"
}

Response:
{
    "session_id": "unique-session-id",
    "response": "AI-enhanced agricultural advice",
    "intent": "crop_cultivation",
    "confidence": 0.9,
    "language_code": "en-US",
    "response_time": 1.2
}
```

#### **B. Voice Chat API (Full Conversation)**
```
POST /api/voice-chat/
Content-Type: application/json

Request:
{
    "audio_data": "base64-encoded-audio-bytes",
    "session_id": "optional-session-id",
    "language_code": "auto"
}

Response:
{
    "session_id": "unique-session-id",
    "transcribed_text": "What user said",
    "response": "AI agricultural advice",
    "audio_response": "base64-encoded-mp3-audio",
    "intent": "pest_control",
    "confidence": 0.95,
    "language_code": "hi-IN",
    "response_time": 2.1
}
```

#### **C. Speech-to-Text API**
```
POST /api/speech-to-text/
Content-Type: application/json

Request:
{
    "audio_data": "base64-encoded-audio-bytes",
    "language_code": "auto"
}

Response:
{
    "transcribed_text": "Converted speech text",
    "language_code": "ta-IN",
    "confidence": 0.9
}
```

#### **D. Other Endpoints**
```
GET /api/languages/              # Supported languages
GET /api/health/                 # Health check
GET /api/history/{session_id}/   # Chat history
GET /conversation-mode/          # Conversation mode page
```

## 🚀 **3. Installation & Setup**

### **Step 1: Create Django Project**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Create Django project
django-admin startproject crop_chatbot
cd crop_chatbot

# Create chatbot app
python manage.py startapp chatbot
```

### **Step 2: Database Setup**
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Populate knowledge base
python manage.py populate_knowledge_base
python manage.py add_crop_knowledge
```

### **Step 3: Start Server**
```bash
python manage.py runserver 0.0.0.0:8000
```

## 🔗 **4. Frontend Integration**

### **A. Base API URL**
```javascript
const API_BASE_URL = 'http://localhost:8000';  // Development
// const API_BASE_URL = 'https://your-domain.com';  // Production
```

### **B. JavaScript Integration Examples**

#### **Text Chat Integration:**
```javascript
async function sendTextMessage(message, sessionId = null, languageCode = 'auto') {
    const response = await fetch(`${API_BASE_URL}/api/chat/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            session_id: sessionId,
            language_code: languageCode
        })
    });
    
    return await response.json();
}
```

#### **Voice Chat Integration:**
```javascript
async function sendVoiceMessage(audioBlob, sessionId = null, languageCode = 'auto') {
    const audioBase64 = await blobToBase64(audioBlob);
    
    const response = await fetch(`${API_BASE_URL}/api/voice-chat/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            audio_data: audioBase64,
            session_id: sessionId,
            language_code: languageCode
        })
    });
    
    return await response.json();
}

function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}
```

#### **Speech-to-Text Integration:**
```javascript
async function convertSpeechToText(audioBlob, languageCode = 'auto') {
    const audioBase64 = await blobToBase64(audioBlob);
    
    const response = await fetch(`${API_BASE_URL}/api/speech-to-text/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            audio_data: audioBase64,
            language_code: languageCode
        })
    });
    
    return await response.json();
}
```

### **C. Language Support Integration:**
```javascript
async function getSupportedLanguages() {
    const response = await fetch(`${API_BASE_URL}/api/languages/`);
    const data = await response.json();
    return data.languages;
}
```

## 🛡️ **5. CORS Configuration**

The backend includes CORS headers for frontend integration:

```python
# In settings.py
CORS_ALLOW_ALL_ORIGINS = True  # Development only
CORS_ALLOW_CREDENTIALS = True

# For production, use specific origins:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "https://your-frontend-domain.com",
# ]
```

## 📱 **6. Frontend Requirements**

### **Required Frontend Features:**
- Audio recording capability (MediaRecorder API)
- Base64 encoding/decoding
- Fetch API for HTTP requests
- Audio playback for voice responses

### **Optional Enhancements:**
- WebRTC for better audio quality
- Service Worker for offline support
- Progressive Web App features

## 🔧 **7. Configuration for Different Environments**

### **Development:**
```env
DEBUG=True
CORS_ALLOW_ALL_ORIGINS=True
```

### **Production:**
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## 🎯 **8. Testing the Integration**

### **Quick Test Commands:**
```bash
# Test health endpoint
curl http://localhost:8000/api/health/

# Test text chat
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How to grow tomatoes?", "language_code": "en-US"}'

# Test languages
curl http://localhost:8000/api/languages/
```

## 📋 **9. Integration Checklist**

- [ ] Backend server running on port 8000
- [ ] Environment variables configured
- [ ] Google Cloud credentials set up
- [ ] Gemini API key configured
- [ ] Database migrations completed
- [ ] Knowledge base populated
- [ ] CORS configured for frontend domain
- [ ] API endpoints tested
- [ ] Frontend can reach backend APIs
- [ ] Audio recording/playback working

This complete backend provides all the AI-powered agricultural assistance features with multi-language support, voice capabilities, and Gemini AI integration ready for frontend integration.