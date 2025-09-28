# 🚀 Running Crop Crystalline Chatbot in Cursor (Windows) with WSL

## 📋 Prerequisites
- Windows 10/11 with WSL2 installed
- Cursor IDE installed on Windows
- Ubuntu/Debian running in WSL
- Project located in WSL filesystem

## 🔧 Step-by-Step WSL + Cursor Setup

### **1. Install WSL Extension in Cursor**
```bash
1. Open Cursor IDE on Windows
2. Ctrl+Shift+X (Extensions)
3. Search for "WSL" 
4. Install "WSL" extension by Microsoft
5. Restart Cursor if prompted
```

### **2. Connect to WSL**
```bash
# Method A: Direct connection
1. Ctrl+Shift+P → "WSL: Connect to WSL"
2. Select your WSL distribution (Ubuntu/Debian)
3. New Cursor window opens connected to WSL

# Method B: Open project folder
1. Ctrl+Shift+P → "WSL: Open Folder in WSL"
2. Navigate to your project: /home/bala/chatbot
3. Click "OK"
```

### **3. Set Up Python in WSL**
```bash
# In Cursor connected to WSL:
1. Ctrl+Shift+P → "Python: Select Interpreter"
2. Choose: /home/bala/chatbot/venv/bin/python
3. Or browse to: \\wsl$\Ubuntu\home\bala\chatbot\venv\bin\python
```

### **4. Configure Terminal for WSL**
```bash
# Cursor will automatically use WSL terminal
# Terminal path should show: /home/bala/chatbot
# If not, check bottom-left corner of Cursor shows "WSL: Ubuntu"
```

## 🔧 Updated Configuration Files

### **Update .vscode/settings.json for WSL**
```json
{
    "python.defaultInterpreterPath": "/home/bala/chatbot/venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "terminal.integrated.defaultProfile.linux": "bash",
    "remote.WSL.fileWatcher.polling": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "django.snippets.enabled": true,
    "files.associations": {
        "*.html": "django-html"
    },
    "emmet.includeLanguages": {
        "django-html": "html"
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": false
    },
    "files.watcherExclude": {
        "**/venv/**": true,
        "**/__pycache__/**": true
    }
}
```

### **Update .vscode/launch.json for WSL**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django: Run Server (WSL)",
            "type": "python",
            "request": "launch",
            "program": "/home/bala/chatbot/manage.py",
            "args": [
                "runserver",
                "0.0.0.0:8000"
            ],
            "django": true,
            "env": {
                "DJANGO_SETTINGS_MODULE": "crop_chatbot.settings"
            },
            "console": "integratedTerminal",
            "justMyCode": false,
            "python": "/home/bala/chatbot/venv/bin/python"
        },
        {
            "name": "Django: Debug Tests (WSL)",
            "type": "python",
            "request": "launch",
            "program": "/home/bala/chatbot/manage.py",
            "args": [
                "test",
                "--verbosity=2"
            ],
            "django": true,
            "env": {
                "DJANGO_SETTINGS_MODULE": "crop_chatbot.settings"
            },
            "console": "integratedTerminal",
            "python": "/home/bala/chatbot/venv/bin/python"
        }
    ]
}
```

## 🌐 Accessing Your Application

### **From Windows Browser**
```bash
# Your Django server runs in WSL but accessible from Windows:
http://localhost:8000
# or
http://127.0.0.1:8000

# If port forwarding issues, use WSL IP:
# In WSL terminal: ip addr show eth0
# Then use: http://[WSL_IP]:8000
```

## 🔧 File System Access

### **Windows ↔ WSL File Access**
```bash
# From Windows Explorer:
\\wsl$\Ubuntu\home\bala\chatbot

# From WSL to Windows:
/mnt/c/Users/bala/

# Google Cloud JSON Key:
# Copy from: C:\Users\bala\Downloads\logical-bloom-472314-d4-3b1dc56de916.json
# To WSL: /home/bala/chatbot/credentials/google-cloud-key.json
```

### **Copy Google Cloud Key to WSL**
```bash
# In WSL terminal (from Cursor):
mkdir -p /home/bala/chatbot/credentials
cp /mnt/c/Users/bala/Downloads/logical-bloom-472314-d4-3b1dc56de916.json /home/bala/chatbot/credentials/google-cloud-key.json

# Update .env file:
GOOGLE_APPLICATION_CREDENTIALS=/home/bala/chatbot/credentials/google-cloud-key.json
```

## 🚀 Running the Project

### **1. Open Project in Cursor WSL**
```bash
1. Open Cursor on Windows
2. Ctrl+Shift+P → "WSL: Open Folder in WSL"
3. Navigate to: /home/bala/chatbot
4. Click "Select Folder"
```

### **2. Activate Environment & Run**
```bash
# Terminal in Cursor (should automatically be WSL bash):
cd /home/bala/chatbot
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### **3. Access from Windows**
```bash
# Open Windows browser:
http://localhost:8000
```

## 🎯 Development Workflow

### **Editing Files**
```bash
# All files edited in Cursor on Windows
# Changes automatically sync to WSL
# Hot reload works perfectly with Django
```

### **Terminal Commands**
```bash
# All Django commands run in WSL terminal:
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py test
```

### **Debugging**
```bash
# F5 to start debugging
# Breakpoints work across Windows/WSL boundary
# Variables inspection works normally
```

## 🔍 Troubleshooting WSL + Cursor

### **Common Issues & Solutions**

**1. "Cannot find Python interpreter"**
```bash
# Solution:
1. Ensure connected to WSL (check bottom-left: "WSL: Ubuntu")
2. Ctrl+Shift+P → "Python: Select Interpreter"
3. Browse to: /home/bala/chatbot/venv/bin/python
```

**2. "Port 8000 not accessible from Windows"**
```bash
# Solution:
1. Run server with: python manage.py runserver 0.0.0.0:8000
2. Check Windows firewall settings
3. Restart WSL: wsl --shutdown, then reopen
```

**3. "File changes not detected"**
```bash
# Solution:
1. Add to settings.json: "remote.WSL.fileWatcher.polling": true
2. Restart Cursor
3. Ensure WSL2 (not WSL1): wsl -l -v
```

**4. "Google Cloud credentials not found"**
```bash
# Solution:
1. Copy JSON file to WSL filesystem
2. Use Linux paths in .env: /home/bala/chatbot/credentials/
3. Restart Django server
```

## 🎨 Cursor Features in WSL

### **AI Assistant Works Perfectly**
```python
# Ctrl+K still works for AI code generation
# Ctrl+L for AI chat
# All Cursor AI features work in WSL mode
```

### **Extensions in WSL**
```bash
# Install these in WSL mode:
1. Python (Microsoft)
2. Django Template
3. GitLens
4. Thunder Client (for API testing)
```

### **Git Integration**
```bash
# Git commands work in WSL terminal
# Cursor shows git status from WSL
# Commit/push directly from Cursor
```

## 🎉 Performance Tips

### **Optimize WSL Performance**
```bash
# In C:\Users\bala\.wslconfig:
[wsl2]
memory=4GB
processors=2
swap=2GB
```

### **File Watching**
```bash
# Add to .vscode/settings.json:
"files.watcherExclude": {
    "**/venv/**": true,
    "**/__pycache__/**": true,
    "**/node_modules/**": true
}
```

## ✅ Verification Checklist

- [ ] Cursor connected to WSL (shows "WSL: Ubuntu" in bottom-left)
- [ ] Python interpreter set to WSL path
- [ ] Terminal shows Linux prompt
- [ ] Django server accessible at localhost:8000
- [ ] File changes trigger auto-reload
- [ ] Debugging works with F5
- [ ] Google Cloud credentials copied to WSL

## 🚀 You're Ready!

Your **Windows Cursor + WSL setup** is now optimized for Django development with:
- ✅ **Seamless file editing** on Windows
- ✅ **Linux environment** for Django
- ✅ **AI assistance** with Cursor features
- ✅ **Full debugging** support
- ✅ **Port forwarding** to Windows browser

**Happy coding with the best of both worlds!** 🌟