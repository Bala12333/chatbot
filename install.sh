#!/bin/bash

# Crop Crystalline Chatbot Installation Script

echo "🌱 Installing Crop Crystalline Chatbot..."

# Check Python version
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
python3 -m pip install -r requirements.txt

# Check Django installation
python3 -c "import django; print(f'Django {django.get_version()} installed')"

# Run Django checks
echo "🔍 Running Django system checks..."
python3 manage.py check

# Create and run migrations
echo "📊 Setting up database..."
python3 manage.py makemigrations
python3 manage.py migrate

# Create superuser (skip if exists)
echo "👤 Setting up admin user..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python3 manage.py shell

# Populate knowledge base
echo "📚 Populating knowledge base..."
python3 manage.py populate_knowledge_base
python3 manage.py populate_knowledge_base --language=es-ES
python3 manage.py populate_knowledge_base --language=hi-IN

# Collect static files
echo "📁 Collecting static files..."
python3 manage.py collectstatic --noinput

echo "✅ Installation completed successfully!"
echo ""
echo "🚀 To start the development server:"
echo "   python3 manage.py runserver"
echo ""
echo "🌐 Then visit: http://127.0.0.1:8000"
echo "👑 Admin panel: http://127.0.0.1:8000/admin"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "⚠️  Note: For production, please:"
echo "   1. Change the admin password"
echo "   2. Set up Google Cloud credentials in .env"
echo "   3. Configure proper SECRET_KEY"
echo "   4. Set DEBUG=False"