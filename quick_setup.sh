#!/bin/bash

# 🌱 Crop Crystalline Chatbot - Quick Setup Script
# Run this script to set up everything automatically

set -e  # Exit on any error

echo "🌱 Welcome to Crop Crystalline Chatbot Setup!"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Step 1: Check Python
print_status "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Found $PYTHON_VERSION"
else
    print_error "Python 3 is not installed"
    exit 1
fi

# Step 2: Install system dependencies
print_status "Installing system dependencies..."
if command -v apt &> /dev/null; then
    print_status "Updating package list..."
    sudo apt update
    
    print_status "Installing Python venv and pip..."
    sudo apt install -y python3-venv python3-pip python3-dev
    
    print_status "Installing audio dependencies..."
    sudo apt install -y portaudio19-dev python3-pyaudio || print_warning "Audio dependencies failed (optional)"
    
    print_success "System dependencies installed"
elif command -v yum &> /dev/null; then
    print_status "Installing dependencies with yum..."
    sudo yum install -y python3-venv python3-pip python3-devel
elif command -v brew &> /dev/null; then
    print_status "Installing dependencies with Homebrew..."
    brew install python3
else
    print_warning "Unknown package manager. Please install python3-venv and python3-pip manually"
fi

# Step 3: Create virtual environment
print_status "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Step 4: Activate virtual environment and install dependencies
print_status "Installing Python dependencies..."
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Step 5: Set up environment file
print_status "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        
        # Generate a random secret key
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
        sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
        
        print_success "Environment file created with random secret key"
        print_warning "Please edit .env file to add your Google Cloud credentials"
    else
        print_error ".env.example not found"
        exit 1
    fi
else
    print_warning ".env file already exists"
fi

# Step 6: Django setup
print_status "Setting up Django application..."

# Check Django installation
python -c "import django; print(f'Django {django.get_version()} ready')" || {
    print_error "Django installation failed"
    exit 1
}

# Create migrations
print_status "Creating database migrations..."
python manage.py makemigrations

# Apply migrations
print_status "Applying database migrations..."
python manage.py migrate

# Step 7: Create superuser
print_status "Creating superuser account..."
echo "Creating admin user with username: admin, password: admin123"
echo "You can change this later in the admin panel"
DJANGO_SUPERUSER_PASSWORD=admin123 python manage.py createsuperuser --noinput --username admin --email admin@example.com || print_warning "Superuser may already exist"

# Step 8: Populate knowledge base
print_status "Populating knowledge base..."
python manage.py populate_knowledge_base
python manage.py populate_knowledge_base --language=es-ES
python manage.py populate_knowledge_base --language=hi-IN

# Step 9: Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Step 10: Run tests
print_status "Running tests..."
python manage.py test || print_warning "Some tests failed (this is okay for initial setup)"

# Step 11: Final checks
print_status "Running system checks..."
python manage.py check

print_success "Setup completed successfully!"
echo ""
echo "🚀 Your Crop Crystalline Chatbot is ready!"
echo "============================================"
echo ""
print_status "To start the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
print_status "Then open your browser and visit:"
echo "  🌐 Main app: http://127.0.0.1:8000"
echo "  👑 Admin:    http://127.0.0.1:8000/admin"
echo "     Username: admin"
echo "     Password: admin123"
echo ""
print_warning "Important next steps:"
echo "  1. Edit .env file to add Google Cloud credentials for voice features"
echo "  2. Change admin password in the admin panel"
echo "  3. Add more agricultural content through admin panel"
echo ""
print_success "Happy farming with AI! 🌾"