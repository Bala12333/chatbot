# 🌱 Crop Crystalline Chatbot - Complete Setup Guide

## 📋 Prerequisites

Before starting, ensure you have:
- **Ubuntu/Debian system** (or similar Linux distribution)
- **Internet connection** for downloading packages
- **Terminal access** with sudo privileges

## 🚀 Step-by-Step Setup

### Step 1: Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python virtual environment and pip
sudo apt install -y python3.12-venv python3-pip python3-dev

# Install additional dependencies for audio processing
sudo apt install -y portaudio19-dev python3-pyaudio

# Verify installation
python3 --version
```

### Step 2: Create Virtual Environment

```bash
# Navigate to your project directory
cd /path/to/crop-crystalline-chatbot

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (you should see (venv) in your prompt)
which python
```

### Step 3: Install Python Dependencies

```bash
# With virtual environment activated
pip install --upgrade pip
pip install -r requirements.txt

# Verify Django installation
python -c "import django; print(f'Django {django.get_version()} installed successfully')"
```

### Step 4: Set Up Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit the .env file with your settings
nano .env
```

**Edit `.env` file with these values:**
```env
# Django settings
SECRET_KEY=your-very-secure-secret-key-change-this-in-production
DEBUG=True

# Google Cloud credentials (we'll set this up later)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id

# Dialogflow settings (optional)
DIALOGFLOW_PROJECT_ID=your-dialogflow-project-id
DIALOGFLOW_LANGUAGE_CODE=en-US
```

### Step 5: Initialize Database

```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
# Enter: username=admin, email=admin@example.com, password=admin123 (or your choice)
```

### Step 6: Populate Knowledge Base

```bash
# Load English knowledge base
python manage.py populate_knowledge_base

# Load Spanish knowledge base
python manage.py populate_knowledge_base --language=es-ES

# Load Hindi knowledge base
python manage.py populate_knowledge_base --language=hi-IN

# You can add more languages as needed
```

### Step 7: Collect Static Files

```bash
# Collect static files for serving
python manage.py collectstatic --noinput
```

### Step 8: Test the Application

```bash
# Run system checks
python manage.py check

# Run tests
python manage.py test

# Start development server
python manage.py runserver
```

### Step 9: Access the Application

1. **Open your web browser**
2. **Navigate to:** http://127.0.0.1:8000
3. **Admin panel:** http://127.0.0.1:8000/admin (use credentials from Step 5)

## 🌐 Google Cloud Setup (Optional but Recommended)

For full voice functionality, set up Google Cloud services:

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your Project ID

### Step 2: Enable APIs

Enable these APIs in your Google Cloud project:
- **Cloud Speech-to-Text API**
- **Cloud Text-to-Speech API**
- **Dialogflow API** (optional)

```bash
# Using gcloud CLI (if installed)
gcloud services enable speech.googleapis.com
gcloud services enable texttospeech.googleapis.com
gcloud services enable dialogflow.googleapis.com
```

### Step 3: Create Service Account

1. Go to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Name: `crop-chatbot-service`
4. Grant roles:
   - **Dialogflow API Client**
   - **Cloud Speech Client**
   - **Cloud Text-to-Speech Client**
5. Create and download JSON key file

### Step 4: Configure Credentials

```bash
# Place your service account key in the project
mkdir -p credentials/
mv ~/Downloads/your-service-account-key.json credentials/

# Update .env file
nano .env
```

Update these lines in `.env`:
```env
GOOGLE_APPLICATION_CREDENTIALS=./credentials/your-service-account-key.json
GOOGLE_CLOUD_PROJECT_ID=your-actual-project-id
```

### Step 5: Test Voice Features

```bash
# Restart the server to load new credentials
python manage.py runserver
```

Now test voice input/output in the web interface!

## 🐳 Alternative: Docker Setup

If you prefer Docker:

### Step 1: Install Docker

```bash
# Install Docker
sudo apt install -y docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, then test
docker --version
```

### Step 2: Run with Docker

```bash
# Build and start all services
docker-compose up --build

# Access at http://localhost:8000
```

## 🧪 Testing Your Setup

### Basic Functionality Test

1. **Open** http://127.0.0.1:8000
2. **Type** "How do I treat tomato blight?"
3. **Expect** agricultural advice response
4. **Try** different languages from dropdown
5. **Test** voice input (microphone button)

### Admin Panel Test

1. **Open** http://127.0.0.1:8000/admin
2. **Login** with your superuser credentials
3. **Browse** Knowledge base entries
4. **View** Chat sessions and messages

### API Test

```bash
# Test chat API
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What fertilizer should I use?", "language_code": "en-US"}'

# Test health endpoint
curl http://127.0.0.1:8000/api/health/
```

## 🔧 Troubleshooting

### Common Issues

**Django Import Error:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install Django
```

**Database Migration Issues:**
```bash
# Reset migrations
rm -rf chatbot/migrations/
python manage.py makemigrations chatbot
python manage.py migrate
```

**Google Cloud Authentication:**
```bash
# Test credentials
python -c "from google.cloud import speech; print('Google Cloud credentials OK')"
```

**Permission Denied:**
```bash
# Fix file permissions
chmod +x install.sh
chmod +x manage.py
```

## 📊 Production Deployment

For production deployment:

1. **Set** `DEBUG=False` in `.env`
2. **Use** PostgreSQL instead of SQLite
3. **Configure** proper web server (nginx + gunicorn)
4. **Set up** SSL certificates
5. **Configure** firewall and security groups
6. **Use** Docker or cloud services

## 🎯 What's Next?

After successful setup:

1. **Customize** knowledge base with your agricultural content
2. **Add** more languages
3. **Integrate** with weather APIs
4. **Set up** monitoring and logging
5. **Deploy** to production environment

## 🆘 Need Help?

If you encounter issues:

1. **Check** the logs: `python manage.py runserver --verbosity=2`
2. **Review** Django admin for errors
3. **Test** individual components
4. **Verify** Google Cloud setup
5. **Check** file permissions and virtual environment

---

🌾 **Happy farming with your AI assistant!** 🌱