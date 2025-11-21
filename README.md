# 🌱 Crop Crystalline Chatbot

An AI-powered, multilingual advisory chatbot for farmers. It provides instant information on crop management, pests, and soil health via both text and voice, aiming to be fast, accessible, and easy to use.

## ✨ Features

- **🗣️ Multilingual Support**: Text and voice chat in 8+ languages (English, Spanish, French, German, Portuguese, Hindi, Chinese, Arabic)
- **🎤 Voice Input/Output**: Speak your questions and hear responses back
- **🌾 Agricultural Expertise**: Knowledge base covering:
  - Crop diseases and treatment
  - Pest identification and control
  - Fertilizer recommendations
  - Weather-related farming advice
  - Soil health management
- **📱 Mobile Responsive**: Works perfectly on phones, tablets, and desktops
- **⚡ Fast Response**: < 3 seconds response time for 95% of queries
- **🔄 Real-time Chat**: Instant messaging interface
- **📊 Admin Dashboard**: Manage knowledge base and view chat analytics

## 🛠️ Technology Stack

- **Backend**: Django 4.2+ (Python 3.8+)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI Services**: 
  - Google Cloud Speech-to-Text
  - Google Cloud Text-to-Speech
  - Google Cloud Dialogflow (optional)
- **Deployment**: Docker-ready

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Google Cloud account (for speech services)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd crop-crystalline-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Google Cloud credentials and settings
   ```

5. **Set up Google Cloud credentials**
   - Create a service account in Google Cloud Console
   - Download the JSON key file
   - Set `GOOGLE_APPLICATION_CREDENTIALS` in `.env` to the path of your key file

6. **Run setup script**
   ```bash
   python setup.py
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Open your browser**
   - Visit: http://127.0.0.1:8000
   - Admin panel: http://127.0.0.1:8000/admin

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Google Cloud credentials
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id

# Dialogflow settings (optional)
DIALOGFLOW_PROJECT_ID=your-dialogflow-project-id
DIALOGFLOW_LANGUAGE_CODE=en-US
```

### Google Cloud Setup

1. **Enable APIs**:
   - Cloud Speech-to-Text API
   - Cloud Text-to-Speech API
   - Dialogflow API (optional)

2. **Create Service Account**:
   - Go to Google Cloud Console → IAM & Admin → Service Accounts
   - Create a new service account
   - Grant necessary permissions
   - Download JSON key file

3. **Set up Dialogflow** (optional):
   - Create a new Dialogflow project
   - Configure intents and entities for agricultural queries
   - Link to your Google Cloud project

## 📚 API Endpoints

### Chat API
- `POST /api/chat/` - Send text message
- `POST /api/voice-chat/` - Send voice message
- `GET /api/history/<session_id>/` - Get chat history
- `GET /api/languages/` - Get supported languages
- `GET /api/health/` - Health check

### Request Examples

**Text Chat**:
```json
{
  "message": "How do I treat tomato blight?",
  "session_id": "optional-session-id",
  "language_code": "en-US"
}
```

**Voice Chat**:
```json
{
  "audio_data": "base64-encoded-audio",
  "session_id": "optional-session-id", 
  "language_code": "en-US"
}
```

## 🗃️ Database Models

### KnowledgeBase
Stores agricultural knowledge and advice:
- `category`: Type of advice (crop_diseases, pest_identification, etc.)
- `topic`: Specific topic or problem
- `question_patterns`: Common question patterns
- `answer`: Response text
- `language_code`: Language of the entry

### ChatSession
Tracks user chat sessions:
- `session_id`: Unique session identifier
- `language_code`: User's preferred language
- `created_at`: Session start time

### ChatMessage
Stores chat history:
- `session`: Link to chat session
- `message_type`: 'user' or 'bot'
- `content`: Message text
- `audio_file`: Optional audio file
- `response_time`: Bot response time

## 🌍 Adding New Languages

1. **Add language support**:
   ```python
   # In chatbot/views.py, update supported_languages view
   {'code': 'new-lang', 'name': 'Language Name', 'native_name': 'Native Name'}
   ```

2. **Populate knowledge base**:
   ```bash
   python manage.py populate_knowledge_base --language=new-lang
   ```

3. **Update frontend**:
   - Add translations in `static/js/chatbot.js`
   - Update language selector in template

## 🐳 Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python setup.py

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

## 📊 Monitoring

- Response times are tracked in the database
- Use Django admin to view chat analytics
- Health check endpoint: `/api/health/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request


## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the admin panel for chat logs

## 🔮 Future Enhancements

- [ ] Integration with weather APIs
- [ ] Image-based pest identification
- [ ] Crop planning calendar
- [ ] Push notifications
- [ ] Offline mode improvements
- [ ] Advanced analytics dashboard
- [ ] Integration with agricultural databases

---

Made with ❤️ for farmers worldwide 🌾
