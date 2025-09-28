"""
Views for the chatbot application.
Handles HTTP requests for text and voice interactions with the agricultural chatbot.
Provides comprehensive multilingual support with automatic language detection.
"""

# Import necessary libraries for Django web framework and chatbot functionality
import json  # JSON parsing for API requests and responses
import time  # Time tracking for response time measurement
import uuid  # Unique identifier generation for chat sessions
import base64  # Base64 encoding/decoding for audio data transfer
from django.shortcuts import render  # Template rendering for web pages
from django.http import JsonResponse, HttpResponse  # HTTP response objects
from django.views.decorators.csrf import csrf_exempt  # CSRF protection bypass for APIs
from django.views.decorators.http import require_http_methods  # HTTP method restrictions
from django.utils.decorators import method_decorator  # Decorator utilities
from django.views import View  # Class-based view base class
from django.core.files.base import ContentFile  # File handling for audio storage
from .models import ChatSession, ChatMessage  # Database models for chat data
from .services import ChatbotService  # Core chatbot service with AI capabilities
import logging  # Logging for error tracking and debugging

# Create logger instance for this module
logger = logging.getLogger(__name__)


def index(request):
    """
    Main chatbot interface - serves the web page for farmer interactions.
    Renders the HTML template with voice and text input capabilities.
    """
    return render(request, 'chatbot/index.html')


def conversation_mode(request):
    """
    Conversational speech mode interface - dedicated page for hands-free interaction.
    Provides continuous voice conversation with the agricultural assistant.
    """
    return render(request, 'chatbot/conversation_mode.html')


@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(View):
    """
    API endpoint for text-based chat interactions.
    
    FUNCTIONALITY:
    - Receives text messages from farmers in any supported language
    - Auto-detects the language from user input
    - Searches agricultural knowledge base for relevant information
    - Returns response in the SAME language as user input
    - Tracks session and conversation history
    """
    
    def __init__(self):
        """Initialize the chatbot service for text processing."""
        super().__init__()
        # Create chatbot service instance with all AI capabilities
        self.chatbot_service = ChatbotService()
    
    def post(self, request):
        """
        Handle text chat messages with automatic language detection and response.
        
        REQUEST FORMAT:
        {
            "message": "धान की खेती कैसे करें?",  // User question in any language
            "session_id": "optional-session-id",    // Session tracking (auto-generated if missing)
            "language_code": "auto"                  // 'auto' for detection or specific code
        }
        
        RESPONSE FORMAT:
        {
            "session_id": "unique-session-id",
            "response": "धान की खेती के लिए...",     // Answer in user's language
            "intent": "crop_diseases",               // Category of question
            "confidence": 0.95,                      // Match confidence (0.0-1.0)
            "language_code": "hi-IN",               // Detected/used language
            "response_time": 0.008                   // Processing time in seconds
        }
        """
        try:
            # Parse JSON request body to extract user input
            data = json.loads(request.body)
            message = data.get('message', '').strip()  # User's agricultural question
            session_id = data.get('session_id')       # Session tracking ID
            language_code = data.get('language_code', 'auto')  # Language preference or auto-detect (default: auto)
            
            # Validate that user provided a message
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            # Create or retrieve existing chat session for conversation tracking
            if not session_id:
                session_id = str(uuid.uuid4())  # Generate unique session ID
            
            # Get or create session in database with language preference
            session, created = ChatSession.objects.get_or_create(
                session_id=session_id,
                defaults={'language_code': language_code if language_code != 'auto' else 'en-US'}
            )
            
            # Start timing for performance monitoring
            start_time = time.time()
            
            # Save user's message to database for history and analytics
            user_message = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=message
            )
            
            # CORE PROCESSING: Send to chatbot service for AI response generation
            # This will:
            # 1. Auto-detect language from user input (always auto-detect)
            # 2. Search agricultural knowledge base for relevant information
            # 3. Generate response in user's native language
            response_data = self.chatbot_service.process_text_message(
                message, session_id, 'auto'  # Always use auto-detection
            )
            
            # Calculate total processing time for performance tracking
            response_time = time.time() - start_time
            
            # Save chatbot's response to database for history
            bot_message = ChatMessage.objects.create(
                session=session,
                message_type='bot',
                content=response_data['text_response'],
                response_time=response_time
            )
            
            # Return complete response to user in their native language
            return JsonResponse({
                'session_id': session_id,                      # Session tracking
                'response': response_data['text_response'],    # Agricultural advice in user's language
                'intent': response_data['intent'],             # Question category (diseases, fertilizer, etc.)
                'confidence': response_data['confidence'],     # How confident the match was
                'language_code': response_data['language_code'], # Language used for response
                'response_time': response_time,                # Performance metric
            })
            
        except json.JSONDecodeError:
            # Handle malformed JSON requests
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            # Log any unexpected errors for debugging
            logger.error(f"Chat API error: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class VoiceChatAPIView(View):
    """
    API endpoint for voice-based chat interactions with automatic language detection.
    
    FUNCTIONALITY:
    - Receives audio from farmers speaking in any supported language
    - Converts speech to text using Google Cloud Speech-to-Text
    - Auto-detects language from transcribed text
    - Searches agricultural knowledge base for relevant information
    - Returns both text and audio response in user's native language
    - Stores audio files for history and quality monitoring
    """
    
    def __init__(self):
        """Initialize the chatbot service for voice processing."""
        super().__init__()
        # Create chatbot service instance with speech capabilities
        self.chatbot_service = ChatbotService()
    
    def post(self, request):
        """
        Handle voice chat messages with speech-to-text and text-to-speech conversion.
        
        REQUEST FORMAT:
        {
            "audio_data": "base64-encoded-audio-bytes",  // User's voice in WebM format
            "session_id": "optional-session-id",         // Session tracking
            "language_code": "auto"                       // 'auto' for detection or specific code
        }
        
        RESPONSE FORMAT:
        {
            "session_id": "unique-session-id",
            "transcribed_text": "धान की खेती कैसे करें?",  // What user said
            "response": "धान की खेती के लिए...",           // Written agricultural advice
            "audio_response": "base64-encoded-mp3",        // Spoken response in user's language
            "intent": "crop_diseases",                     // Question category
            "confidence": 0.95,                           // Match confidence
            "language_code": "hi-IN",                     // Detected language
            "response_time": 1.2                          // Total processing time
        }
        """
        try:
            # Parse JSON request body to extract voice data
            data = json.loads(request.body)
            audio_data_b64 = data.get('audio_data')  # Base64 encoded audio from microphone
            session_id = data.get('session_id')      # Session tracking ID
            language_code = data.get('language_code', 'auto')  # Language hint or auto-detect
            
            # Validate that audio data was provided
            if not audio_data_b64:
                return JsonResponse({'error': 'Audio data is required'}, status=400)
            
            # Decode base64 audio data to raw bytes for Google Cloud processing
            try:
                audio_data = base64.b64decode(audio_data_b64)
            except Exception:
                return JsonResponse({'error': 'Invalid audio data'}, status=400)
            
            # Create or retrieve existing chat session for conversation tracking
            if not session_id:
                session_id = str(uuid.uuid4())  # Generate unique session ID
            
            # Get or create session in database
            session, created = ChatSession.objects.get_or_create(
                session_id=session_id,
                defaults={'language_code': language_code if language_code != 'auto' else 'en-US'}
            )
            
            # Start timing for performance monitoring (includes speech processing)
            start_time = time.time()
            
            # CORE PROCESSING: Send to chatbot service for complete voice interaction
            # This will:
            # 1. Convert speech to text using Google Cloud Speech-to-Text
            # 2. Auto-detect language from transcribed text
            # 3. Search agricultural knowledge base for relevant information
            # 4. Generate text response in user's native language
            # 5. Convert response to speech using Google Cloud Text-to-Speech
            response_data = self.chatbot_service.process_voice_message(
                audio_data, session_id, 'auto'  # Always use auto-detection
            )
            
            # Calculate total processing time (speech-to-text + AI + text-to-speech)
            response_time = time.time() - start_time
            
            # Save user's voice message to database if transcription was successful
            if response_data['transcribed_text']:
                user_message = ChatMessage.objects.create(
                    session=session,
                    message_type='user',
                    content=response_data['transcribed_text']  # Save what user said
                )
                
                # Store original audio file for quality monitoring and playback
                audio_file = ContentFile(audio_data)
                user_message.audio_file.save(
                    f'user_audio_{session_id}_{int(time.time())}.webm',  # WebM format from browser
                    audio_file
                )
            
            # Save chatbot's response to database
            bot_message = ChatMessage.objects.create(
                session=session,
                message_type='bot',
                content=response_data['text_response'],  # Written agricultural advice
                response_time=response_time
            )
            
            # Prepare audio response for transmission back to user
            audio_response_b64 = None
            if response_data['audio_response']:
                # Encode MP3 audio as base64 for JSON transmission
                audio_response_b64 = base64.b64encode(response_data['audio_response']).decode('utf-8')
                
                # Store generated audio file for history and monitoring
                bot_audio_file = ContentFile(response_data['audio_response'])
                bot_message.audio_file.save(
                    f'bot_audio_{session_id}_{int(time.time())}.mp3',  # MP3 format from TTS
                    bot_audio_file
                )
            
            # Return complete voice interaction result to user
            return JsonResponse({
                'session_id': session_id,                         # Session tracking
                'transcribed_text': response_data['transcribed_text'], # What user said
                'response': response_data['text_response'],       # Written agricultural advice
                'audio_response': audio_response_b64,             # Spoken response (base64)
                'intent': response_data['intent'],                # Question category
                'confidence': response_data['confidence'],        # Match confidence
                'language_code': response_data['language_code'],  # Detected/used language
                'response_time': response_time,                   # Total processing time
            })
            
        except json.JSONDecodeError:
            # Handle malformed JSON requests
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            # Log any unexpected errors for debugging
            logger.error(f"Voice chat API error: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SpeechToTextAPIView(View):
    """
    API endpoint for speech-to-text conversion only.
    
    FUNCTIONALITY:
    - Receives audio from users speaking in any supported language
    - Converts speech to text using Google Cloud Speech-to-Text
    - Returns only the transcribed text (no chatbot response)
    - Used for the microphone button in regular chat mode
    """
    
    def __init__(self):
        """Initialize the speech-to-text service."""
        super().__init__()
        self.chatbot_service = ChatbotService()
    
    def post(self, request):
        """
        Handle speech-to-text conversion.
        
        REQUEST FORMAT:
        {
            "audio_data": "base64-encoded-audio-bytes",  // User's voice in WebM format
            "language_code": "auto"                       // 'auto' for detection or specific code
        }
        
        RESPONSE FORMAT:
        {
            "transcribed_text": "धान की खेती कैसे करें?",  // What user said
            "language_code": "hi-IN",                     // Detected language
            "confidence": 0.95                            // Transcription confidence
        }
        """
        try:
            # Parse JSON request body to extract voice data
            data = json.loads(request.body)
            audio_data_b64 = data.get('audio_data')  # Base64 encoded audio from microphone
            language_code = data.get('language_code', 'auto')  # Language hint or auto-detect
            
            # Validate that audio data was provided
            if not audio_data_b64:
                return JsonResponse({'error': 'Audio data is required'}, status=400)
            
            # Decode base64 audio data to raw bytes for Google Cloud processing
            try:
                audio_data = base64.b64decode(audio_data_b64)
            except Exception:
                return JsonResponse({'error': 'Invalid audio data'}, status=400)
            
            # Convert speech to text using Google Cloud Speech-to-Text
            transcribed_text = self.chatbot_service.speech_to_text.transcribe_audio(
                audio_data, language_code if language_code != 'auto' else 'en-US'
            )
            
            if transcribed_text:
                # Detect language from transcribed text if auto-detection was requested
                if language_code == 'auto':
                    detected_language = self.chatbot_service.dialogflow._detect_language(transcribed_text)
                else:
                    detected_language = language_code
                
                return JsonResponse({
                    'transcribed_text': transcribed_text,
                    'language_code': detected_language,
                    'confidence': 0.9  # High confidence for successful transcription
                })
            else:
                return JsonResponse({
                    'error': 'Could not transcribe audio. Please speak more clearly or check your microphone.'
                }, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Speech-to-text API error: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


@require_http_methods(["GET"])
def chat_history(request, session_id):
    """Get chat history for a session."""
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = session.messages.all()
        
        history = []
        for message in messages:
            history.append({
                'type': message.message_type,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'response_time': message.response_time,
            })
        
        return JsonResponse({
            'session_id': session_id,
            'language_code': session.language_code,
            'history': history,
        })
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        logger.error(f"Chat history error: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'Crop Crystalline Chatbot',
        'version': '1.0.0',
    })


@require_http_methods(["GET"])
def supported_languages(request):
    """Get list of supported languages."""
    languages = [
        {'code': 'auto', 'name': 'Auto-detect Language', 'native_name': '🌍 Auto-detect'},
        {'code': 'en-US', 'name': 'English (India)', 'native_name': 'English'},
        {'code': 'hi-IN', 'name': 'Hindi (India)', 'native_name': 'हिन्दी'},
        {'code': 'te-IN', 'name': 'Telugu (India)', 'native_name': 'తెలుగు'},
        {'code': 'pa-IN', 'name': 'Punjabi (India)', 'native_name': 'ਪੰਜਾਬੀ'},
        {'code': 'ta-IN', 'name': 'Tamil (India)', 'native_name': 'தமிழ்'},
        {'code': 'bn-IN', 'name': 'Bengali (India)', 'native_name': 'বাংলা'},
        {'code': 'mr-IN', 'name': 'Marathi (India)', 'native_name': 'मराठी'},
        {'code': 'gu-IN', 'name': 'Gujarati (India)', 'native_name': 'ગુજરાતી'},
        {'code': 'kn-IN', 'name': 'Kannada (India)', 'native_name': 'ಕನ್ನಡ'},
        {'code': 'ml-IN', 'name': 'Malayalam (India)', 'native_name': 'മലയാളം'},
    ]
    
    return JsonResponse({'languages': languages})