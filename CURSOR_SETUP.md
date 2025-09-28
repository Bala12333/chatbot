# 🚀 Running Crop Crystalline Chatbot in Cursor IDE

## 📋 Prerequisites
- Cursor IDE installed
- Python 3.8+ installed on your system
- Git (optional, for version control)

## 🔧 Step-by-Step Setup in Cursor

### 1. **Open Project in Cursor**
```bash
# Method A: Open existing folder
1. Open Cursor IDE
2. File → Open Folder
3. Navigate to your chatbot project folder
4. Select the folder containing manage.py

# Method B: Clone if from Git
1. Ctrl+Shift+P (Command Palette)
2. Type "Git: Clone"
3. Enter repository URL (if applicable)
```

### 2. **Set Up Python Interpreter**
```bash
# In Cursor:
1. Ctrl+Shift+P → "Python: Select Interpreter"
2. Choose "Enter interpreter path manually"
3. Navigate to: ./venv/bin/python (Linux/Mac) or .\venv\Scripts\python.exe (Windows)
4. Or create new venv: Ctrl+Shift+P → "Python: Create Environment"
```

### 3. **Install Dependencies**
```bash
# Open Cursor Terminal (Ctrl+` or View → Terminal)
# Activate virtual environment first:

# On Windows:
.\venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate

# Install packages:
pip install -r requirements.txt
```

### 4. **Configure Environment**
```bash
# In Cursor, create/edit .env file:
1. Right-click in Explorer → New File
2. Name it ".env"
3. Add your configuration:

SECRET_KEY=your-secret-key-here
DEBUG=True
GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-cloud-key.json
GOOGLE_CLOUD_PROJECT_ID=logical-bloom-472314-d4
```

### 5. **Database Setup**
```bash
# In Cursor Terminal:
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py populate_knowledge_base
python manage.py add_crop_knowledge
```

### 6. **Run the Server**
```bash
# In Cursor Terminal:
python manage.py runserver

# Server will start at: http://127.0.0.1:8000
```

## 🎯 Cursor-Specific Features

### **Integrated Terminal**
- `Ctrl+`` to open terminal
- Multiple terminal tabs supported
- Automatic virtual environment detection

### **Python Debugging**
```python
# Create launch.json for debugging:
# .vscode/launch.json (Cursor uses VS Code configs)
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": ["runserver"],
            "django": true,
            "justMyCode": true
        }
    ]
}
```

### **AI Assistant in Cursor**
```bash
# Use Cursor's AI features:
1. Ctrl+K - AI code generation
2. Ctrl+L - Chat with AI about your code
3. Select code + Ctrl+K - AI code modification
4. Comment your intent, then Ctrl+K to generate code
```

### **File Explorer Setup**
```
crop-crystalline-chatbot/
├── 📁 chatbot/              # Main app
├── 📁 crop_chatbot/         # Django project
├── 📁 static/               # CSS, JS files
├── 📁 templates/            # HTML templates
├── 📁 venv/                 # Virtual environment
├── 📄 manage.py             # Django management
├── 📄 requirements.txt      # Dependencies
├── 📄 .env                  # Environment variables
└── 📄 README.md             # Documentation
```

## 🔍 Cursor Development Workflow

### **1. Code with AI Assistance**
```python
# Example: Ask Cursor AI to help add new features
# Select this comment and press Ctrl+K:
# "Add a new management command to export knowledge base to CSV"

# Cursor will generate the code for you!
```

### **2. Debug with Breakpoints**
```python
# In views.py, click left margin to set breakpoints
# Press F5 to start debugging
# Use Debug Console to inspect variables
```

### **3. Run Tests**
```bash
# In Cursor Terminal:
python manage.py test

# Or use Cursor's test runner:
# Ctrl+Shift+P → "Python: Run All Tests"
```

### **4. Git Integration**
```bash
# Cursor has built-in Git support:
# Ctrl+Shift+G - Open Source Control
# Stage, commit, and push directly from IDE
```

## 🎨 Cursor Extensions for Django

### **Recommended Extensions**
```bash
# Install these extensions in Cursor:
1. Python - Microsoft
2. Django - Baptiste Darthenay  
3. HTML CSS Support
4. JavaScript (ES6) code snippets
5. GitLens — Git supercharged
6. Thunder Client (for API testing)
```

## 🧪 Testing in Cursor

### **API Testing with Thunder Client**
```bash
# Install Thunder Client extension
# Create new request:
POST http://127.0.0.1:8000/api/chat/
Content-Type: application/json

{
    "message": "How do I treat rice blast?",
    "language_code": "en-US"
}
```

### **Django Shell in Cursor**
```python
# In terminal:
python manage.py shell

# Test your models interactively:
from chatbot.models import KnowledgeBase
KnowledgeBase.objects.all()
```

## 🔧 Troubleshooting in Cursor

### **Common Issues**

**1. Python Interpreter Not Found**
```bash
# Solution:
1. Ctrl+Shift+P → "Python: Select Interpreter"
2. Browse to your venv/bin/python or venv/Scripts/python.exe
```

**2. Module Import Errors**
```bash
# Solution:
1. Ensure virtual environment is activated
2. Check PYTHONPATH in settings
3. Restart Cursor after changing interpreter
```

**3. Django Server Won't Start**
```bash
# Check:
1. Virtual environment activated
2. Dependencies installed (pip install -r requirements.txt)
3. Database migrated (python manage.py migrate)
4. Port 8000 not in use
```

## 🚀 Production Deployment from Cursor

### **Build Docker Image**
```dockerfile
# Use Cursor's integrated terminal:
docker build -t crop-chatbot .
docker run -p 8000:8000 crop-chatbot
```

### **Deploy to Cloud**
```bash
# Configure deployment directly from Cursor:
# 1. Set up cloud provider CLI
# 2. Use terminal for deployment commands
# 3. Monitor logs in Cursor terminal
```

## 🎯 Cursor Shortcuts for Django Development

| Shortcut | Function |
|----------|----------|
| `Ctrl+Shift+P` | Command Palette |
| `Ctrl+`` | Toggle Terminal |
| `Ctrl+K` | AI Code Generation |
| `Ctrl+L` | Chat with AI |
| `F5` | Start Debugging |
| `Ctrl+Shift+G` | Source Control |
| `Ctrl+P` | Quick File Open |
| `Ctrl+Shift+F` | Search in Files |
| `F12` | Go to Definition |
| `Ctrl+Space` | Trigger IntelliSense |

## 🎉 You're Ready!

Your Crop Crystalline Chatbot is now fully set up in Cursor IDE with:
- ✅ AI-powered code assistance
- ✅ Integrated debugging
- ✅ Terminal and Git integration
- ✅ Django-specific features
- ✅ API testing capabilities

**Start developing with AI assistance at your fingertips!** 🚀