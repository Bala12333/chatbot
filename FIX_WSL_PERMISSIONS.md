# 🔧 Fixing WSL Permissions and PowerShell Issues

## 🚨 Current Issues:
1. PowerShell execution policy blocking script
2. Virtual environment activation permission denied
3. Mixed Windows/Linux file permissions

## ✅ **Solution 1: Use Linux Commands in WSL**

### **Step 1: Fix Virtual Environment Permissions**
```bash
# In WSL terminal (not PowerShell):
cd ~/chatbot
chmod +x venv/bin/activate
chmod +x venv/bin/python
chmod -R +x venv/bin/

# Activate using source (not the activate script directly):
source venv/bin/activate
```

### **Step 2: Verify Setup**
```bash
# Check if in virtual environment (should show (venv)):
source venv/bin/activate
which python
# Should show: /home/bala/chatbot/venv/bin/python

python --version
# Should show Python 3.12.3
```

## ✅ **Solution 2: Fix PowerShell Execution Policy (Alternative)**

### **If you prefer using PowerShell:**
```powershell
# Run PowerShell as Administrator and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then you can run:
& "\\wsl.localhost\Ubuntu\home\bala\chatbot\.venv\Scripts\Activate.ps1"
```

## 🚀 **Recommended Workflow for Cursor + WSL**

### **Step 1: Open Cursor in WSL Mode**
```bash
1. Open Cursor on Windows
2. Ctrl+Shift+P → "WSL: Connect to WSL"
3. Or Ctrl+Shift+P → "WSL: Open Folder in WSL"
4. Navigate to /home/bala/chatbot
```

### **Step 2: Use WSL Terminal in Cursor**
```bash
# In Cursor, open terminal (Ctrl+`)
# Terminal should automatically be in WSL mode
# If not, click the dropdown and select "bash"

cd /home/bala/chatbot
source venv/bin/activate
```

### **Step 3: Run Django**
```bash
# With virtual environment activated:
python manage.py runserver 0.0.0.0:8000
```

## 🔧 **Create Activation Script for Easy Use**

### **Create a simple startup script:**
```bash
# In WSL, create a startup script:
cd ~/chatbot
cat > start_chatbot.sh << 'EOF'
#!/bin/bash
cd /home/bala/chatbot
source venv/bin/activate
echo "🌱 Crop Chatbot Environment Activated!"
echo "Virtual environment: $(which python)"
echo "Django version: $(python -c 'import django; print(django.get_version())')"
echo ""
echo "Available commands:"
echo "  python manage.py runserver 0.0.0.0:8000  # Start server"
echo "  python manage.py shell                   # Django shell"
echo "  python manage.py test                    # Run tests"
echo ""
exec bash
EOF

chmod +x start_chatbot.sh
```

### **Use the startup script:**
```bash
# In WSL terminal:
./start_chatbot.sh
```

## 🎯 **Fix File Permissions Issues**

### **Reset all permissions:**
```bash
cd ~/chatbot
# Fix Python virtual environment permissions:
find venv/ -name "*.py" -exec chmod +x {} \;
chmod +x venv/bin/*

# Fix project file permissions:
find . -name "*.py" -exec chmod +x {} \;
chmod +x manage.py

# Fix shell scripts:
find . -name "*.sh" -exec chmod +x {} \;
```

## 🔄 **Alternative: Recreate Virtual Environment**

### **If permissions are too messed up:**
```bash
cd ~/chatbot
# Remove old virtual environment:
rm -rf venv

# Create new one:
python3 -m venv venv
source venv/bin/activate

# Reinstall packages:
pip install --upgrade pip
pip install -r requirements.txt

# Verify it works:
python manage.py check
```

## 🚀 **Test Everything Works**

### **Complete test sequence:**
```bash
# 1. Activate environment
cd ~/chatbot
source venv/bin/activate

# 2. Check Django
python manage.py check

# 3. Run migrations (if needed)
python manage.py migrate

# 4. Start server
python manage.py runserver 0.0.0.0:8000

# 5. Test in browser (from Windows):
# http://localhost:8000
```

## 🎨 **Cursor Configuration**

### **Update .vscode/tasks.json for easy commands:**
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Django Server",
            "type": "shell",
            "command": "source venv/bin/activate && python manage.py runserver 0.0.0.0:8000",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "options": {
                "cwd": "/home/bala/chatbot"
            },
            "problemMatcher": []
        },
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "source venv/bin/activate && python manage.py test",
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always"
            },
            "options": {
                "cwd": "/home/bala/chatbot"
            }
        },
        {
            "label": "Django Shell",
            "type": "shell", 
            "command": "source venv/bin/activate && python manage.py shell",
            "presentation": {
                "echo": true,
                "reveal": "always"
            },
            "options": {
                "cwd": "/home/bala/chatbot"
            }
        }
    ]
}
```

## ⚡ **Quick Fix Commands**

### **Run these in WSL terminal:**
```bash
# One-liner to fix everything:
cd ~/chatbot && chmod +x venv/bin/* && source venv/bin/activate && python manage.py check

# If that works, start the server:
python manage.py runserver 0.0.0.0:8000
```

## 🎉 **Success Indicators**

You'll know it's working when:
- ✅ Terminal shows `(venv)` prefix
- ✅ `which python` shows `/home/bala/chatbot/venv/bin/python`
- ✅ `python manage.py check` shows no errors
- ✅ Server starts without permission errors
- ✅ http://localhost:8000 loads in Windows browser

## 🆘 **If Still Having Issues**

### **Nuclear option - fresh start:**
```bash
# Complete reset:
cd ~
rm -rf chatbot/venv
cd chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

**Try the first solution (chmod commands) - that should fix it!** 🚀