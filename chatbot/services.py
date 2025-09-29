"""
Google Cloud services integration for speech, text-to-speech, and Dialogflow.
This module provides comprehensive agricultural chatbot services with multilingual support.
"""

# Import necessary libraries for Google Cloud services and Django integration
import os  # Operating system interface for environment variables
import base64  # Base64 encoding/decoding for audio data
import tempfile  # Temporary file handling
from typing import Optional, Tuple  # Type hints for better code documentation
from django.conf import settings  # Django settings configuration
from google.cloud import speech  # Google Cloud Speech-to-Text API
from google.cloud import texttospeech  # Google Cloud Text-to-Speech API
from google.cloud import dialogflow  # Google Cloud Dialogflow API (not actively used)
import google.generativeai as genai  # Google Gemini API
from .models import KnowledgeBase  # Local knowledge base model
import logging  # Logging for error tracking and debugging

# Create logger instance for this module
logger = logging.getLogger(__name__)


class SpeechToTextService:
    """
    Google Cloud Speech-to-Text service integration.
    Converts audio input (voice) into text with multilingual support.
    Specifically designed for Indian farmers speaking various regional languages.
    """
    
    def __init__(self):
        """Initialize the Speech-to-Text client with Google Cloud credentials."""
        # Create Google Cloud Speech client using service account credentials
        self.client = speech.SpeechClient()
    
    def transcribe_audio(self, audio_data: bytes, language_code: str = 'en-US') -> Optional[str]:
        """
        Transcribe audio data to text with automatic language detection.
        
        PROCESS:
        1. Receives raw audio bytes from user's microphone
        2. Configures Google Cloud Speech with primary language + alternatives
        3. Sends audio to Google Cloud for transcription
        4. Returns the most confident transcription result
        
        Args:
            audio_data: Raw audio bytes from user's microphone (WebM Opus format)
            language_code: Primary language code for transcription (defaults to English)
            
        Returns:
            Transcribed text string or None if transcription failed
        """
        try:
            # Supported languages for detection
            valid_language_codes = [
                'en-US', 'hi-IN', 'te-IN', 'pa-IN', 'ta-IN', 'bn-IN', 'mr-IN', 'gu-IN', 'kn-IN', 'ml-IN'
            ]

            # If language_code is 'auto', set up for true auto-detection
            if language_code == 'auto':
                primary_language = 'en-US'  # Can be any from the list
                alternative_language_codes = [code for code in valid_language_codes if code != primary_language]
            elif language_code in valid_language_codes:
                primary_language = language_code
                alternative_language_codes = [code for code in valid_language_codes if code != primary_language]
            else:
                logger.warning(f"Invalid or missing language_code '{language_code}', defaulting to 'en-US'")
                primary_language = 'en-US'
                alternative_language_codes = [code for code in valid_language_codes if code != primary_language]

            # Create audio object from raw bytes for Google Cloud processing
            audio = speech.RecognitionAudio(content=audio_data)

            # Configure speech recognition settings
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code=primary_language,
                alternative_language_codes=alternative_language_codes,
                enable_automatic_punctuation=True,
            )

            # Log config for debugging
            logger.debug(f"Speech-to-text config: {config}")

            response = self.client.recognize(config=config, audio=audio)
            if response.results:
                return response.results[0].alternatives[0].transcript
            return None
        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            logger.error(f"Audio length: {len(audio_data) if audio_data else 0}")
            return None


class TextToSpeechService:
    """
    Google Cloud Text-to-Speech service integration.
    Converts text responses into natural-sounding speech audio.
    Supports multiple Indian languages with native voice synthesis.
    """
    
    def __init__(self):
        """Initialize the Text-to-Speech client with Google Cloud credentials."""
        # Create Google Cloud Text-to-Speech client for voice synthesis
        self.client = texttospeech.TextToSpeechClient()
    
    def synthesize_speech(self, text: str, language_code: str = 'en-US') -> Optional[bytes]:
        """
        Convert text response to natural speech audio in user's native language.
        
        PROCESS:
        1. Receives text response from chatbot knowledge base
        2. Configures voice parameters (language, gender, speed)
        3. Sends text to Google Cloud for voice synthesis
        4. Returns high-quality MP3 audio bytes
        
        Args:
            text: Text response to convert to speech (agricultural advice/answer)
            language_code: Language code for voice synthesis (matches user's language)
            
        Returns:
            MP3 audio bytes for playback or None if synthesis failed
        """
        try:
            # Validate language_code
            valid_language_codes = [
                'en-US', 'hi-IN', 'te-IN', 'pa-IN', 'ta-IN', 'bn-IN', 'mr-IN', 'gu-IN', 'kn-IN', 'ml-IN'
            ]
            if not language_code or language_code not in valid_language_codes:
                logger.warning(f"Invalid or missing language_code '{language_code}', defaulting to 'en-US'")
                language_code = 'en-US'

            # Prepare text input for Google Cloud Text-to-Speech processing
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Set a default voice name for each language (optional, but avoids empty voice errors)
            default_voice_names = {
                'en-US': 'en-US-Wavenet-D',
                'hi-IN': 'hi-IN-Wavenet-A',
                'te-IN': 'te-IN-Wavenet-A',
                'pa-IN': 'pa-IN-Wavenet-A',
                'ta-IN': 'ta-IN-Wavenet-A',
                'bn-IN': 'bn-IN-Wavenet-A',
                'mr-IN': 'mr-IN-Wavenet-A',
                'gu-IN': 'gu-IN-Wavenet-A',
                'kn-IN': 'kn-IN-Wavenet-A',
                'ml-IN': 'ml-IN-Wavenet-A',
            }
            voice_name = default_voice_names.get(language_code, '')

            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
                ssml_gender=texttospeech.SsmlVoiceGender.MALE,
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0,
            )

            logger.debug(f"Text-to-speech config: language_code={language_code}, voice_name={voice_name}")

            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            return response.audio_content
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            logger.error(f"Text: {text}, Language: {language_code}")
            return None


class GeminiService:
    """
    Google Gemini AI service integration for enhanced agricultural intelligence.
    Combines local knowledge base with Gemini's advanced reasoning capabilities.
    """
    
    def __init__(self):
        """Initialize Gemini AI service with API key."""
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            logger.warning("Gemini API key not configured, using local knowledge base only")
            self.model = None
    
    def generate_response(self, user_question: str, language_code: str, local_knowledge: str = None) -> dict:
        """
        Generate AI response using Gemini + local knowledge base hybrid approach.
        
        Args:
            user_question: User's agricultural question
            language_code: Language for response
            local_knowledge: Relevant knowledge from local DB (optional)
            
        Returns:
            Dictionary with AI response, intent, and confidence
        """
        try:
            if not self.model:
                # Fallback to local knowledge if Gemini not available
                return self._fallback_response(user_question, language_code, local_knowledge)
            
            # Create enhanced prompt combining local knowledge with Gemini's capabilities
            prompt = self._create_enhanced_prompt(user_question, language_code, local_knowledge)
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            return {
                'intent': 'ai_enhanced_response',
                'fulfillment_text': response.text,
                'confidence': 0.9,
                'parameters': {'source': 'gemini_hybrid'},
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._fallback_response(user_question, language_code, local_knowledge)
    
    def _create_enhanced_prompt(self, question: str, language_code: str, local_knowledge: str = None) -> str:
        """Create enhanced prompt for Gemini with agricultural context."""
        
        language_names = {
            'en-US': 'English',
            'hi-IN': 'Hindi',
            'ta-IN': 'Tamil', 
            'te-IN': 'Telugu',
            'bn-IN': 'Bengali',
            'mr-IN': 'Marathi',
            'gu-IN': 'Gujarati',
            'pa-IN': 'Punjabi',
            'kn-IN': 'Kannada',
            'ml-IN': 'Malayalam'
        }
        
        response_language = language_names.get(language_code, 'English')
        
        prompt = f"""You are a friendly agricultural assistant helping farmers. Give practical, easy-to-understand advice.

Context: {local_knowledge if local_knowledge else "General agricultural knowledge"}

User Question: {question}

Instructions:
1. Keep response SHORT and SWEET (50-100 words maximum)
2. Use simple, everyday language farmers can understand
3. Give 2-3 main actionable points only
4. Include specific dosages/amounts when needed
5. Respond in {response_language} language
6. Be warm and encouraging in tone
7. Use emojis sparingly for friendliness

Give a brief, helpful answer:"""

        return prompt
    
    def _fallback_response(self, question: str, language_code: str, local_knowledge: str = None) -> dict:
        """Fallback response when Gemini is unavailable."""
        if local_knowledge:
            return {
                'intent': 'local_knowledge',
                'fulfillment_text': local_knowledge,
                'confidence': 0.8,
                'parameters': {'source': 'local_database'},
            }
        else:
            # Return generic helpful response
            return {
                'intent': 'general_help',
                'fulfillment_text': self._get_general_help_response(language_code),
                'confidence': 0.5,
                'parameters': {'source': 'fallback'},
            }
    
    def _get_general_help_response(self, language_code: str) -> str:
        """Get general help response in user's language."""
        responses = {
            'en-US': "I'm here to help with your farming questions! Please ask about specific crops, diseases, fertilizers, or soil management for detailed advice.",
            'hi-IN': "मैं आपके कृषि प्रश्नों में मदद के लिए यहाँ हूँ! कृपया विशिष्ट फसलों, बीमारियों, उर्वरकों या मिट्टी प्रबंधन के बारे में पूछें।",
            'ta-IN': "உங்கள் விவசாய கேள்விகளுக்கு உதவ நான் இங்கே இருக்கிறேன்! குறிப்பிட்ட பயிர்கள், நோய்கள், உரங்கள் அல்லது மண் மேலாண்மை பற்றி கேளுங்கள்।"
        }
        return responses.get(language_code, responses['en-US'])


class DialogflowService:
    """Google Cloud Dialogflow service integration."""
    
    def __init__(self):
        self.project_id = settings.DIALOGFLOW_PROJECT_ID
        self.gemini_service = GeminiService()  # Add Gemini integration
        if not self.project_id:
            logger.warning("Dialogflow project ID not configured")
    
    def detect_intent(self, text: str, session_id: str, language_code: str = 'en-US') -> dict:
        """
        Detect intent using Dialogflow.
        
        Args:
            text: User input text
            session_id: Unique session identifier
            language_code: Language code for processing
            
        Returns:
            Dictionary containing intent and response
        """
        # Skip Dialogflow and use local knowledge base directly for better performance
        logger.info("Using local knowledge base for faster response")
        return self._fallback_to_knowledge_base(text, language_code)
    
    def _fallback_to_knowledge_base(self, text: str, language_code: str) -> dict:
        """
        Enhanced fallback to local knowledge base with Gemini AI integration.
        
        HYBRID AI RESPONSE STRATEGY:
        1. Search local knowledge base for exact matches
        2. If found, use as context for Gemini AI enhancement
        3. If not found, use Gemini AI for general agricultural advice
        4. Always return response in user's native language
        """
        text_lower = text.lower()
        
        # Get knowledge entries for the user's native language first
        native_entries = KnowledgeBase.objects.filter(language_code=language_code)
        
        # Try all passes with native language content first
        native_result = self._search_knowledge_entries(text_lower, native_entries, True)
        if native_result:
            # Handle special soil-specific advice
            if (native_result.get('intent') == 'soil_health_special' and 
                native_result.get('parameters', {}).get('needs_soil_advice')):
                soil_advice = self._get_soil_specific_advice(language_code, text_lower)
                if soil_advice:
                    native_result['fulfillment_text'] = soil_advice
                    native_result['intent'] = 'soil_health'
                    del native_result['parameters']['needs_soil_advice']
            
            # Enhance local knowledge with Gemini AI
            enhanced_result = self.gemini_service.generate_response(
                text, language_code, native_result['fulfillment_text']
            )
            return enhanced_result
        
        # If no native content found, search English content
        if language_code != 'en-US':
            english_entries = KnowledgeBase.objects.filter(language_code='en-US')
            english_result = self._search_knowledge_entries(text_lower, english_entries, False)
            if english_result:
                # Handle special soil-specific advice for English content
                if (english_result.get('intent') == 'soil_health_special' and 
                    english_result.get('parameters', {}).get('needs_soil_advice')):
                    soil_advice = self._get_soil_specific_advice(language_code, text_lower)
                    if soil_advice:
                        english_result['fulfillment_text'] = soil_advice
                        english_result['intent'] = 'soil_health'
                        del english_result['parameters']['needs_soil_advice']
                        return english_result
                
                # Enhance English knowledge with Gemini AI in user's language
                enhanced_result = self.gemini_service.generate_response(
                    text, language_code, english_result['fulfillment_text']
                )
                return enhanced_result
        
        # No local knowledge found - use Gemini AI directly
        gemini_result = self.gemini_service.generate_response(text, language_code)
        if gemini_result and gemini_result.get('fulfillment_text'):
            return gemini_result
        
        # Final fallback to default response in user's language
        return {
            'intent': 'default_fallback',
            'fulfillment_text': self._get_default_response(language_code),
            'confidence': 0.5,
            'parameters': {},
        }
    
    def _search_knowledge_entries(self, text_lower: str, knowledge_entries, is_native: bool) -> dict:
        """
        Search knowledge entries with 4-pass system.
        
        Args:
            text_lower: User input in lowercase
            knowledge_entries: QuerySet of knowledge entries to search
            is_native: Whether these are native language entries
        
        Returns:
            Match result dictionary or None if no match
        """
        # First pass: Direct pattern matching (most specific)
        for entry in knowledge_entries:
            patterns = entry.question_patterns.lower().split('\n')
            for pattern in patterns:
                pattern = pattern.strip()
                if pattern and pattern in text_lower:
                    return {
                        'intent': entry.category,
                        'fulfillment_text': entry.answer,
                        'confidence': 0.95,
                        'parameters': {},
                    }
        
        # Second pass: Keyword matching with higher weight for specific crops
        specific_crop_terms = {
            'apple': ['apple', 'apples', 'apple crops', 'apple cultivation', 'apple farming'],
            'rice': ['rice', 'paddy', 'rice soil', 'rice cultivation', 'rice growing'],
            'rotation': ['crop rotation', 'rotation', 'crop cycle', 'farming rotation']
        }
        
        for crop_type, terms in specific_crop_terms.items():
            if any(term in text_lower for term in terms):
                for entry in knowledge_entries:
                    if crop_type.lower() in entry.topic.lower() or crop_type.lower() in entry.question_patterns.lower():
                        return {
                            'intent': entry.category,
                            'fulfillment_text': entry.answer,
                            'confidence': 0.9,
                            'parameters': {},
                        }
        
        # Third pass: Topic-based matching
        for entry in knowledge_entries:
            topic_words = entry.topic.lower().split()
            question_words = entry.question_patterns.lower().split()
            all_words = topic_words + question_words
            
            # Check for significant word overlap
            text_words = text_lower.split()
            common_words = set(all_words) & set(text_words)
            significant_words = [word for word in common_words if len(word) > 3]
            
            if len(significant_words) >= 1:
                return {
                    'intent': entry.category,
                    'fulfillment_text': entry.answer,
                    'confidence': 0.8,
                    'parameters': {},
                }
        
        # Fourth pass: Category-based matching with soil type recognition
        category_keywords = {
            'disease': 'crop_diseases',
            'pest': 'pest_identification', 
            'fertilizer': 'fertilizer_recommendations',
            'weather': 'weather_advice',
            'soil': 'soil_health',
            'cultivation': 'general',
            'farming': 'general'
        }
        
        # Special handling for soil-specific questions (like sandy soil crops)
        soil_keywords = ['மணல்மண்', 'sandy soil', 'soil type', 'मिट्टी', 'మట్టి', 'soil', 'sand']
        if any(keyword in text_lower for keyword in soil_keywords):
            # Return soil-specific advice in user's language
            # Note: We need to get language_code from the calling function
            return {
                'intent': 'soil_health_special',
                'fulfillment_text': 'SOIL_SPECIFIC_ADVICE_NEEDED',
                'confidence': 0.85,
                'parameters': {'needs_soil_advice': True, 'text_lower': text_lower},
            }
        
        for keyword, category in category_keywords.items():
            if keyword in text_lower:
                entries = knowledge_entries.filter(category=category)
                if entries.exists():
                    entry = entries.first()
                    return {
                        'intent': entry.category,
                        'fulfillment_text': entry.answer,
                        'confidence': 0.7,
                        'parameters': {},
                    }
        
        # Only show general crop types if specifically asking about crop types
        crop_keywords = ['crop', 'crops', 'types', 'varieties', 'kinds']
        general_words = ['what', 'which', 'list', 'name', 'different', 'all']
        
        if (any(keyword in text_lower for keyword in crop_keywords) and 
            any(word in text_lower for word in general_words) and
            len(text_lower.split()) <= 6):  # Only for short, general queries
            return {
                'intent': 'crop_information',
                'fulfillment_text': self._get_crop_types_response('en-US' if not is_native else 'native'),
                'confidence': 0.6,
                'parameters': {},
            }
        
        # Return None if no match found (let caller handle fallback)
        return None
    
    def _get_crop_types_response(self, language_code: str) -> str:
        """Get crop types response in the specified language."""
        crop_responses = {
            'en-US': """Here are the main types of crops I can help you with:

🌾 **Cereal Crops**: Rice, Wheat, Corn (Maize), Barley, Oats
🫘 **Legume Crops**: Soybeans, Lentils, Chickpeas, Beans, Peas  
🥕 **Root Crops**: Potatoes, Sweet Potatoes, Carrots, Radishes
🍅 **Vegetable Crops**: Tomatoes, Peppers, Onions, Cabbage, Lettuce
🍎 **Fruit Crops**: Apples, Oranges, Bananas, Grapes, Berries
🌻 **Oil Crops**: Sunflower, Canola, Peanuts, Sesame
🌿 **Fiber Crops**: Cotton, Flax, Hemp
☕ **Beverage Crops**: Coffee, Tea, Cocoa

I have detailed knowledge about diseases, pests, fertilization, and management for rice, wheat, corn, and tomatoes. Ask me specific questions like "How to treat rice blast?" or "What fertilizer for corn?"

What crop would you like to know more about?""",
            
            'es-ES': """Aquí están los principales tipos de cultivos con los que puedo ayudarte:

🌾 **Cereales**: Arroz, Trigo, Maíz, Cebada, Avena
🫘 **Leguminosas**: Soja, Lentejas, Garbanzos, Frijoles
🥕 **Tubérculos**: Papas, Camotes, Zanahorias
🍅 **Hortalizas**: Tomates, Pimientos, Cebollas, Repollo
🍎 **Frutales**: Manzanas, Naranjas, Plátanos, Uvas

Tengo conocimiento detallado sobre arroz, trigo, maíz y tomates. ¿Sobre qué cultivo te gustaría saber más?""",
            
            'hi-IN': """यहाँ मुख्य फसलों के प्रकार हैं जिनमें मैं आपकी मदद कर सकता हूँ:

🌾 **अनाज**: चावल, गेहूं, मक्का, जौ
🫘 **दलहन**: सोयाबीन, मसूर, चना, राजमा
🥕 **कंद**: आलू, शकरकंद, गाजर
🍅 **सब्जियां**: टमाटर, मिर्च, प्याज, पत्तागोभी
🍎 **फल**: सेब, संतरा, केला, अंगूर

मेरे पास चावल, गेहूं, मक्का और टमाटर की विस्तृत जानकारी है। आप क्या जानना चाहते हैं?"""
        }
        return crop_responses.get(language_code, crop_responses['en-US'])

    def _get_default_response(self, language_code: str) -> str:
        """
        Get comprehensive default response in user's native language.
        
        NATIVE LANGUAGE SUPPORT:
        - Provides detailed agricultural guidance in user's language
        - Includes specific crop examples and farming advice
        - Maintains cultural context for Indian farming
        """
        default_responses = {
            'en-US': """I'm here to help with your farming questions! You can ask me about:

🌾 **Crop Diseases**: Rice blast, wheat rust, corn borer, tomato blight
🌱 **Fertilizer Advice**: NPK ratios, organic fertilizers, micronutrients  
🐛 **Pest Control**: Integrated pest management, natural remedies
🌧️ **Weather Advice**: Planting times, irrigation management
🌍 **Soil Health**: pH balance, organic matter, nutrient management

Feel free to ask specific questions like "How to treat rice blast?" or "What fertilizer for wheat?"
What would you like to know about farming?""",

            'hi-IN': """मैं आपके कृषि संबंधी प्रश्नों में मदद के लिए यहाँ हूँ! आप मुझसे पूछ सकते हैं:

🌾 **फसल की बीमारियां**: चावल ब्लास्ट, गेहूं का रतुआ, मक्का का बोरर, टमाटर की झुलसा
🌱 **उर्वरक सलाह**: NPK अनुपात, जैविक खाद, सूक्ष्म पोषक तत्व
🐛 **कीट नियंत्रण**: एकीकृत कीट प्रबंधन, प्राकृतिक उपचार
🌧️ **मौसम सलाह**: बुआई का समय, सिंचाई प्रबंधन
🌍 **मिट्टी स्वास्थ्य**: pH संतुलन, जैविक पदार्थ, पोषक तत्व प्रबंधन

आप विशिष्ट प्रश्न पूछ सकते हैं जैसे "चावल ब्लास्ट का इलाज कैसे करें?" या "गेहूं के लिए कौन सा उर्वरक?"
आप खेती के बारे में क्या जानना चाहते हैं?""",

            'ta-IN': """விவசायம் பற்றிய உங்கள் கேள்விகளுக்கு உதவ நான் இங்கே இருக்கிறேன்! நீங்கள் என்னிடம் கேட்கலாம்:

🌾 **பயிர் நோய்கள்**: அரிசி பிளாஸ்ட், கோதுமை துரு, சோளம் துளைப்பான், தக்காளி வாடல்
🌱 **உர ஆலோசனை**: NPK விகிதம், இயற்கை உரங்கள், நுண்ணூட்டச்சத்துகள்
🐛 **பூச்சி கட்டுப்பாடு**: ஒருங்கிணைந்த பூச்சி மேலாண்மை, இயற்கை தீர்வுகள்
🌧️ **வானிலை ஆலோசனை**: விதைப்பு நேரம், நீர்ப்பாசன மேலாண்மை
🌍 **மண் ஆரோக்கியம்**: pH சமநிலை, கரிம பொருள், ஊட்டச்சத்து மேலாண்மை

"அரிசி பிளாஸ்ட் எப்படி குணப்படுத்துவது?" அல்லது "கோதுமைக்கு என்ன உரம்?" போன்ற குறிப்பிட்ட கேள்விகளைக் கேட்கலாம்.
விவசாயத்தைப் பற்றி நீங்கள் என்ன தெரிந்து கொள்ள விரும்புகிறீர்கள்?""",

            'te-IN': """వ్యవసాయ ప్రశ్నలకు సహాయం చేయడానికి నేను ఇక్కడ ఉన్నాను! మీరు నన్ను అడగవచ్చు:

🌾 **పంట వ్యాధులు**: వరి బ్లాస్ట్, గోధుమ తుప్పు, మొక్కజొన్న రంధ్రకృమి, టమోటా వాడిపోవడం
🌱 **ఎరువుల సలహా**: NPK నిష్పత్తి, సేంద్రీయ ఎరువులు, సూక్ష్మ పోషకాలు
🐛 **కీటక నియంత్రణ**: సమగ్ర కీటక నిర్వహణ, సహజ పరిష్కారాలు
🌧️ **వాతావరణ సలహా**: విత్తన సమయం, నీటిపారుదల నిర్వహణ
🌍 **మట్టి ఆరోగ్యం**: pH సమతుల్యత, కర్బన పదార్థం, పోషక నిర్వహణ

"వరి బ్లాస్ట్ ఎలా చికిత్స చేయాలి?" లేదా "గోధుమలకు ఏ ఎరువు?" వంటి నిర్దిష్ట ప్రశ్నలు అడగవచ్చు.
వ్యవసాయం గురించి మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?""",

            'bn-IN': """আমি আপনার কৃষি সংক্রান্ত প্রশ্নের সাহায্য করতে এখানে আছি! আপনি আমাকে জিজ্ঞাসা করতে পারেন:

🌾 **ফসলের রোগ**: ধান ব্লাস্ট, গমের মরিচা, ভুট্টার পোকা, টমেটো ঝলসানো
🌱 **সার পরামর্শ**: NPK অনুপাত, জৈব সার, অণুপুষ্টি
🐛 **কীটপতঙ্গ নিয়ন্ত্রণ**: সমন্বিত কীটপতঙ্গ ব্যবস্থাপনা, প্রাকৃতিক প্রতিকার
🌧️ **আবহাওয়া পরামর্শ**: রোপণের সময়, সেচ ব্যবস্থাপনা
🌍 **মাটির স্বাস্থ্য**: pH ভারসাম্য, জৈব পদার্থ, পুষ্টি ব্যবস্থাপনা

আপনি নির্দিষ্ট প্রশ্ন করতে পারেন যেমন "ধান ব্লাস্ট কীভাবে চিকিত্সা করবেন?" বা "গমের জন্য কোন সার?"
চাষাবাদ সম্পর্কে আপনি কী জানতে চান?""",

            'mr-IN': """मी तुमच्या शेती संबंधी प्रश्नांमध्ये मदत करण्यासाठी इथे आहे! तुम्ही मला विचारू शकता:

🌾 **पीक रोग**: तांदूळ ब्लास्ट, गव्हाचा गंज, मक्याचा पोरा, टोमॅटो मुरड
🌱 **खत सल्ला**: NPK गुणोत्तर, सेंद्रिय खते, सूक्ष्म पोषक
🐛 **कीटक नियंत्रण**: एकात्मिक कीटक व्यवस्थापन, नैसर्गिक उपाय
🌧️ **हवामान सल्ला**: पेरणीचा वेळ, सिंचन व्यवस्थापन
🌍 **माती आरोग्य**: pH संतुलन, सेंद्रिय पदार्थ, पोषक व्यवस्थापन

तुम्ही विशिष्ट प्रश्न विचारू शकता जसे "तांदूळ ब्लास्टचा उपचार कसा करावा?" किंवा "गव्हासाठी कोणते खत?"
शेतीबद्दल तुम्हाला काय जाणून घ्यायचे आहे?""",

            'gu-IN': """હું તમારા ખેતીના પ્રશ્નોમાં મદદ કરવા અહીં છું! તમે મને પૂછી શકો:

🌾 **પાકના રોગ**: ચોખાનો બ્લાસ્ટ, ઘઉંનો કાટ, મકાઈનો કીડો, ટમેટાનું મરડું
🌱 **ખાતર સલાહ**: NPK ગુણોત્તર, કાર્બનિક ખાતર, સૂક્ષ્મ પોષક તત્વો
🐛 **જીવાત નિયંત્રણ**: સંકલિત જીવાત વ્યવસ્થાપન, કુદરતી ઉપાય
🌧️ **હવામાન સલાહ**: વાવેતરનો સમય, સિંચાઈ વ્યવસ્થાપન
🌍 **માટીની સ્વાસ્થ્ય**: pH સંતુલન, કાર્બનિક દ્રવ્ય, પોષક વ્યવસ્થાપન

તમે વિશિષ્ટ પ્રશ્નો પૂછી શકો જેવા કે "ચોખાના બ્લાસ્ટની સારવાર કેવી રીતે કરવી?" અથવા "ઘઉં માટે કયું ખાતર?"
ખેતી વિશે તમે શું જાણવા માંગો છો?""",

            'pa-IN': """ਮੈਂ ਤੁਹਾਡੇ ਖੇਤੀ ਸੰਬੰਧੀ ਸਵਾਲਾਂ ਵਿੱਚ ਮਦਦ ਕਰਨ ਲਈ ਇੱਥੇ ਹਾਂ! ਤੁਸੀਂ ਮੈਨੂੰ ਪੁੱਛ ਸਕਦੇ ਹੋ:

🌾 **ਫਸਲ ਦੀਆਂ ਬਿਮਾਰੀਆਂ**: ਚਾਵਲ ਬਲਾਸਟ, ਕਣਕ ਦਾ ਜੰਗ, ਮੱਕੀ ਦਾ ਕੀੜਾ, ਟਮਾਟਰ ਦਾ ਮੁਰਝਾਉਣਾ
🌱 **ਖਾਦ ਸਲਾਹ**: NPK ਅਨੁਪਾਤ, ਜੈਵਿਕ ਖਾਦ, ਸੂਖਮ ਪੋਸ਼ਕ ਤੱਤ
🐛 **ਕੀੜੇ ਨਿਯੰਤਰਣ**: ਏਕੀਕ੍ਰਿਤ ਕੀੜੇ ਪ੍ਰਬੰਧਨ, ਕੁਦਰਤੀ ਉਪਚਾਰ
🌧️ **ਮੌਸਮ ਸਲਾਹ**: ਬੀਜਣ ਦਾ ਸਮਾਂ, ਸਿੰਚਾਈ ਪ੍ਰਬੰਧਨ
🌍 **ਮਿੱਟੀ ਦੀ ਸਿਹਤ**: pH ਸੰਤੁਲਨ, ਜੈਵਿਕ ਪਦਾਰਥ, ਪੋਸ਼ਕ ਪ੍ਰਬੰਧਨ

ਤੁਸੀਂ ਖਾਸ ਸਵਾਲ ਪੁੱਛ ਸਕਦੇ ਹੋ ਜਿਵੇਂ "ਚਾਵਲ ਬਲਾਸਟ ਦਾ ਇਲਾਜ ਕਿਵੇਂ ਕਰੀਏ?" ਜਾਂ "ਕਣਕ ਲਈ ਕਿਹੜੀ ਖਾਦ?"
ਖੇਤੀ ਬਾਰੇ ਤੁਸੀਂ ਕੀ ਜਾਣਨਾ ਚਾਹੁੰਦੇ ਹੋ?""",

            'kn-IN': """ನಿಮ್ಮ ಕೃಷಿ ಪ್ರಶ್ನೆಗಳಿಗೆ ಸಹಾಯ ಮಾಡಲು ನಾನು ಇಲ್ಲಿದ್ದೇನೆ! ನೀವು ನನ್ನನ್ನು ಕೇಳಬಹುದು:

🌾 **ಬೆಳೆ ರೋಗಗಳು**: ಅಕ್ಕಿ ಬ್ಲಾಸ್ಟ್, ಗೋಧಿ ತುಕ್ಕು, ಜೋಳದ ಹುಳು, ಟೊಮೇಟೊ ಬಾಡುವಿಕೆ
🌱 **ಗೊಬ್ಬರ ಸಲಹೆ**: NPK ಅನುಪಾತ, ಜೈವಿಕ ಗೊಬ್ಬರ, ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶಗಳು
🐛 **ಕೀಟ ನಿಯಂತ್ರಣ**: ಸಮಗ್ರ ಕೀಟ ನಿರ್ವಹಣೆ, ನೈಸರ್ಗಿಕ ಪರಿಹಾರಗಳು
🌧️ **ಹವಾಮಾನ ಸಲಹೆ**: ಬಿತ್ತನೆ ಸಮಯ, ನೀರಾವರಿ ನಿರ್ವಹಣೆ
🌍 **ಮಣ್ಣಿನ ಆರೋಗ್ಯ**: pH ಸಮತೋಲನ, ಜೈವಿಕ ಪದಾರ್ಥ, ಪೋಷಕ ನಿರ್ವಹಣೆ

ನೀವು ನಿರ್ದಿಷ್ಟ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಬಹುದು ಉದಾಹರಣೆಗೆ "ಅಕ್ಕಿ ಬ್ಲಾಸ್ಟ್ ಅನ್ನು ಹೇಗೆ ಚಿಕಿತ್ಸೆ ಮಾಡುವುದು?" ಅಥವಾ "ಗೋಧಿಗೆ ಯಾವ ಗೊಬ್ಬರ?"
ಕೃಷಿಯ ಬಗ್ಗೆ ನೀವು ಏನು ತಿಳಿದುಕೊಳ್ಳಲು ಬಯಸುತ್ತೀರಿ?""",

            'ml-IN': """നിങ്ങളുടെ കൃഷിയുമായി ബന്ധപ്പെട്ട ചോദ്യങ്ങളിൽ സഹായിക്കാൻ ഞാൻ ഇവിടെയുണ്ട്! നിങ്ങൾക്ക് എന്നോട് ചോദിക്കാം:

🌾 **വിള രോഗങ്ങൾ**: അരി ബ്ലാസ്റ്റ്, ഗോതമ്പ് തുരുമ്പ്, ചോളം പുഴു, തക്കാളി വാടൽ
🌱 **വള ഉപദേശം**: NPK അനുപാതം, ജൈവ വള, സൂക്ഷ്മ പോഷകങ്ങൾ
🐛 **കീട നിയന്ത്രണം**: സമഗ്ര കീട നിർവ്വഹണം, പ്രകൃതിദത്ത പരിഹാരങ്ങൾ
🌧️ **കാലാവസ്ഥാ ഉപദേശം**: നടീൽ സമയം, ജലസേചന നിർവ്വഹണം
🌍 **മണ്ണിന്റെ ആരോഗ്യം**: pH സന്തുലനം, ജൈവ പദാർത്ഥം, പോഷക നിർവ്വഹണം

നിങ്ങൾക്ക് നിർദ്ദിഷ്ട ചോദ്യങ്ങൾ ചോദിക്കാം ഉദാഹരണത്തിന് "അരി ബ്ലാസ്റ്റ് എങ്ങനെ ചികിത്സിക്കാം?" അല്ലെങ്കിൽ "ഗോതമ്പിന് ഏത് വള?"
കൃഷിയെക്കുറിച്ച് നിങ്ങൾ എന്താണ് അറിയാൻ ആഗ്രഹിക്കുന്നത്?""",

        }
        return default_responses.get(language_code, default_responses['en-US'])
    
    def _translate_response_to_native_language(self, english_text: str, target_language: str) -> str:
        """
        Translate English agricultural content to user's native language.
        
        TRANSLATION STRATEGY:
        1. Use pre-defined agricultural translations for common terms
        2. Maintain technical accuracy for farming concepts
        3. Provide context-appropriate responses for each language
        4. Fallback to English if specific translation not available
        
        Args:
            english_text: Original English agricultural advice
            target_language: User's native language code
            
        Returns:
            Translated agricultural advice in user's native language
        """
        
        # Agricultural translation templates for common responses
        agricultural_translations = {
            'hi-IN': {
                # Apple cultivation translation
                'apple_cultivation': """सेब की खेती भारत में:

**मुख्य क्षेत्र**: हिमाचल प्रदेश, जम्मू और कश्मीर, उत्तराखंड, अरुणाचल प्रदेश
**जलवायु**: ठंडी समशीतोष्ण जलवायु, 1000-2000 मीटर ऊंचाई, 100-200 ठंडे घंटे

**लोकप्रिय किस्में**:
🍎 रेड डिलीशियस - सबसे लोकप्रिय, अच्छा भंडारण
🍎 रॉयल डिलीशियस - अधिक उत्पादन, रोग प्रतिरोधी
🍎 गोल्डन डिलीशियस - मीठा, प्रसंस्करण के लिए अच्छा
🍎 गाला - जल्दी पकने वाला, अच्छा रंग
🍎 फूजी - देर से पकने वाला, उत्कृष्ट संरक्षण गुणवत्ता

**मिट्टी की आवश्यकताएं**:
- अच्छी जल निकासी वाली दोमट मिट्टी, pH 6.0-7.0
- जलभराव वाले क्षेत्रों से बचें
- अच्छी जैविक पदार्थ सामग्री

**रोपण**: जून-जुलाई, दूरी 4x4 मीटर या 5x5 मीटर
**कटाई**: सितंबर-नवंबर किस्म के अनुसार
**उत्पादन**: परिपक्व बागों में 15-25 टन प्रति हेक्टेयर""",

                # Rice blast translation
                'rice_blast': """चावल का ब्लास्ट रोग मैग्नापोर्थे ओराइजे कवक के कारण होता है। लक्षणों में पत्तियों पर हीरे के आकार के धब्बे शामिल हैं जो भूरे या भूरे रंग के होते हैं। गंभीर संक्रमण से उत्पादन में काफी नुकसान हो सकता है।

**नियंत्रण उपाय**:
- प्रतिरोधी किस्मों का उपयोग करें
- उचित बीज उपचार
- संतुलित उर्वरक का प्रयोग
- खेत की सफाई बनाए रखें
- आवश्यकता पड़ने पर कवकनाशी का छिड़काव करें""",

                # Corn fertilizer translation  
                'corn_fertilizer': """मक्का उर्वरक कार्यक्रम: 150-200 किग्रा नाइट्रोजन, 60-80 किग्रा फास्फोरस, 40-60 किग्रा पोटाश प्रति हेक्टेयर। नाइट्रोजन को तीन भागों में बांटें: बुआई के समय 1/3, 4-6 सप्ताह बाद 1/3, और तासेल निकलने के समय 1/3।

**जैविक खाद**: 10-15 टन गोबर की खाद या कंपोस्ट प्रति हेक्टेयर
**सूक्ष्म पोषक तत्व**: जिंक सल्फेट 25 किग्रा/हेक्टेयर""",

                # Pest control translation
                'pest_control': """कीट नियंत्रण के लिए एकीकृत कीट प्रबंधन (IPM) अपनाएं:

**प्राकृतिक तरीके**:
- नीम का तेल या नीम की खली का उपयोग
- फसल चक्र अपनाएं
- प्राकृतिक शत्रुओं को संरक्षित करें
- फेरोमोन ट्रैप का उपयोग

**रासायनिक नियंत्रण**:
- केवल आवश्यकता पड़ने पर ही कीटनाशी का उपयोग करें
- सुरक्षा निर्देशों का पालन करें
- प्रतीक्षा अवधि का सम्मान करें"""
            },
            
            'ta-IN': {
                'apple_cultivation': """இந்தியாவில் ஆப்பிள் சாகுபடி:

**முக்கிய பகுதிகள்**: இமாச்சல பிரதேசம், ஜம்மு காஷ்மீர், உத்தராகண்ட், அருணாச்சல பிரதேசம்
**காலநிலை**: குளிர்ந்த மிதமான காலநிலை, 1000-2000 மீ உயரம், 100-200 குளிர் மணிநேரங்கள்

**பிரபலமான வகைகள்**:
🍎 ரெட் டெலிசியஸ் - மிகவும் பிரபலம், நல்ல சேமிப்பு
🍎 ராயல் டெலிசியஸ் - அதிக மகசூல், நோய் எதிர்ப்பு
🍎 கோல்டன் டெலிசியஸ் - இனிப்பு, செயலாக்கத்திற்கு நல்லது

**மண் தேவைகள்**:
- நன்கு வடிகால் களிமண் மண், pH 6.0-7.0
- நீர்த்தேக்க பகுதிகளைத் தவிர்க்கவும்
- நல்ல கரிம பொருள் உள்ளடக்கம்""",

                'rice_blast': """அரிசி பிளாஸ்ட் நோய் மாக்னபோர்த்தே ஓரைசே பூஞ்சையால் ஏற்படுகிறது। அறிகுறிகளில் இலைகளில் வைர வடிவ புள்ளிகள் இருக்கும்.

**கட்டுப்பாட்டு நடவடிக்கைகள்**:
- எதிர்ப்பு சக்தி கொண்ட வகைகளைப் பயன்படுத்துங்கள்
- சரியான விதை சிகிச்சை
- சமநிலையான உரம் பயன்பாடு""",

                'corn_fertilizer': """மக்காச்சோள உர திட்டம்: ஹெக்டேருக்கு 150-200 கிலோ நைட்ரஜன், 60-80 கிலோ பாஸ்பரஸ், 40-60 கிலோ பொட்டாஷ். நைட்ரஜனை மூன்று பாகங்களாகப் பிரிக்கவும்."""
            },
            
            'te-IN': {
                'apple_cultivation': """భారతదేశంలో ఆపిల్ సాగు:

**ప్రధాన ప్రాంతాలు**: హిమాచల్ ప్రదేశ్, జమ్మూ కాశ్మీర్, ఉత్తరాఖండ్, అరుణాచల్ ప్రదేశ్
**వాతావరణం**: చల్లని సమశీతోష్ణ వాతావరణం, 1000-2000 మీ ఎత్తు

**ప్రసిద్ధ రకాలు**:
🍎 రెడ్ డెలిషియస్ - అత్యంత ప్రసిద్ధం, మంచి నిల్వ
🍎 రాయల్ డెలిషియస్ - అధిక దిగుబడి, వ్యాధి నిరోధకత

**మట్టి అవసరాలు**:
- బాగా పారుదల కలిగిన లోమీ మట్టి, pH 6.0-7.0
- నీటి మునిగిన ప్రాంతాలను తప్పించండి""",

                'rice_blast': """వరి బ్లాస్ట్ వ్యాధి మాగ్నాపోర్థే ఒరైజే ఫంగస్ వల్ల వస్తుంది। లక్షణాలలో ఆకులపై వజ్రాకార మచ్చలు ఉంటాయి।

**నియంత్రణ చర్యలు**:
- నిరోధక రకాలను ఉపయోగించండి
- సరైన విత్తన చికిత్స
- సమతుల్య ఎరువుల వాడకం""",

                'corn_fertilizer': """మొక్కజొన్న ఎరువుల కార్యక్రమం: హెక్టారుకు 150-200 కిలోలు నైట్రోజన్, 60-80 కిలోలు ఫాస్పరస్, 40-60 కిలోలు పొటాష్."""
            }
        }
        
        # Simple keyword-based translation matching
        text_lower = english_text.lower()
        
        if target_language in agricultural_translations:
            translations = agricultural_translations[target_language]
            
            # Check for specific agricultural content patterns
            if 'apple cultivation' in text_lower or 'apple' in text_lower:
                if 'apple_cultivation' in translations:
                    return translations['apple_cultivation']
            
            elif 'rice blast' in text_lower:
                if 'rice_blast' in translations:
                    return translations['rice_blast']
            
            elif 'corn fertilizer' in text_lower or 'maize fertilizer' in text_lower:
                if 'corn_fertilizer' in translations:
                    return translations['corn_fertilizer']
            
            elif 'pest' in text_lower and 'control' in text_lower:
                if 'pest_control' in translations:
                    return translations['pest_control']
        
        # If no specific translation found, return a general response in target language
        general_response = self._get_general_agricultural_advice(target_language)
        return general_response if general_response else english_text
    
    def _get_general_agricultural_advice(self, language_code: str) -> str:
        """Get general agricultural advice in user's language when specific content not available."""
        general_advice = {
            'hi-IN': """मुझे खुशी है कि आप कृषि के बारे में पूछ रहे हैं! मैं निम्नलिखित विषयों में आपकी सहायता कर सकता हूं:

🌾 **फसल की बीमारियां**: चावल ब्लास्ट, गेहूं का रतुआ, मक्का का बोरर
🌱 **उर्वरक सलाह**: NPK अनुपात, जैविक खाद, सूक्ष्म पोषक तत्व
🐛 **कीट नियंत्रण**: एकीकृत कीट प्रबंधन, प्राकृतिक नियंत्रण
🌧️ **मौसम सलाह**: बुआई का समय, सिंचाई प्रबंधन
🌍 **मिट्टी स्वास्थ्य**: pH संतुलन, जैविक पदार्थ, पोषक तत्व प्रबंधन

कृपया अपना विशिष्ट प्रश्न पूछें और मैं आपको विस्तृत जानकारी प्रदान करूंगा।""",
            
            'ta-IN': """விவசायம் பற்றி கேட்டதில் மகிழ்ச்சி! நான் பின்வரும் தலைப்புகளில் உங்களுக்கு உதவ முடியும்:

🌾 **பயிர் நோய்கள்**: அரிசி பிளாஸ்ட், கோதுமை துரு, மக்காச்சோளம் துளைப்பான்
🌱 **உர ஆலோசனை**: NPK விகிதம், இயற்கை உரம், நுண்ணூட்டச்சத்துகள்
🐛 **பூச்சி கட்டுப்பாடு**: ஒருங்கிணைந்த பூச்சி மேலாண்மை
🌧️ **வானிலை ஆலோசனை**: விதைப்பு நேரம், நீர்ப்பாசன மேலாண்மை
🌍 **மண் ஆரோக்கியம்**: pH சமநிலை, கரிம பொருள்

தயவுசெய்து உங்கள் குறிப்பிட்ட கேள்வியைக் கேளுங்கள்.""",
            
            'te-IN': """వ్యవసాయం గురించి అడిగినందుకు సంతోషం! నేను ఈ క్రింది అంశాలలో మీకు సహాయం చేయగలను:

🌾 **పంట వ్యాధులు**: వరి బ్లాస్ట్, గోధుమ తుప్పు, మొక్కజొన్న రంధ్రకృమి
🌱 **ఎరువుల సలహా**: NPK నిష్పత్తి, సేంద్రీయ ఎరువులు, సూక్ష్మ పోషకాలు
🐛 **కీటక నియంత్రణ**: సమగ్ర కీటక నిర్వహణ
🌧️ **వాతావరణ సలహా**: విత్తన సమయం, నీటిపారుదల నిర్వహణ
🌍 **మట్టి ఆరోగ్యం**: pH సమతుల్యత, కర్బన పదార్థం

దయచేసి మీ నిర్దిష్ట ప్రశ్న అడగండి."""
        }
        
        return general_advice.get(language_code, '')
    
    def _get_soil_specific_advice(self, language_code: str, text_lower: str) -> str:
        """
        Get soil-specific agricultural advice in user's native language.
        
        Args:
            language_code: User's language code
            text_lower: User input in lowercase
            
        Returns:
            Soil-specific advice in user's language
        """
        
        # Detect soil type from user input
        sandy_keywords = ['மணல்மண்', 'sandy soil', 'sand', 'sandy', 'मणाल मट्टी', 'ఇసుక మట్టి']
        clay_keywords = ['clay soil', 'heavy soil', 'களிமண்', 'चिकनी मिट्टी', 'బంకమట్టి']
        loamy_keywords = ['loamy soil', 'black soil', 'दोमट मिट्टी', 'లోమీ మట్టి']
        
        soil_advice = {
            'ta-IN': {
                'sandy': """மணல் மண்ணில் பயிரிடுவதற்கான ஆலோசனை:

🌾 **ஏற்ற பயிர்கள்**:
• **தானிய பயிர்கள்**: சிறு தானியங்கள் (சாமை, கேழ்வரகு), கம்பு
• **பருப்பு வகைகள்**: உளுந்து, துவரை, கொண்டை கடலை
• **எண்ணெய் விதைகள்**: நிலக்கடலை, எள், சூரியகாந்தி
• **காய்கறிகள்**: வெங்காயம், பூண்டு, கேரட், முள்ளங்கி
• **பழ மரங்கள்**: மா, பலா, நாரங்கை, பேரீச்சம்

🌱 **மண் மேம்பாட்டு முறைகள்**:
• கால்நடை எரு மற்றும் கம்போஸ்ட் அதிகம் சேர்க்கவும்
• கரிம உரங்களை வருடத்திற்கு 2-3 முறை இடவும்
• பச்சை உரப் பயிர்கள் வளர்க்கவும் (சணப்பு, கொளுஞ்சி)
• நீர் தேக்கும் திறனை அதிகரிக்க மூலக்கூறு கார்பன் சேர்க்கவும்

💧 **நீர் நிர்வாகம்**:
• அடிக்கடி ஆனால் குறைவான நீர் கொடுக்கவும்
• சொட்டு நீர் பாசனம் சிறந்தது
• மல்ச்சிங் செய்து ஈரப்பதம் காக்கவும்

தற்போது எந்த பயிர் பற்றி குறிப்பாக தெரிந்து கொள்ள விரும்புகிறீர்கள்?""",
                
                'clay': """களிமண்ணில் பயிரிடுவதற்கான ஆலோசனை:

🌾 **ஏற்ற பயிர்கள்**:
• **தானிய பயிர்கள்**: நெல், கோதுமை, மக்காச்சோளம்
• **பருப்பு வகைகள்**: அவரை, பட்டாணி, சோயாபீன்
• **காய்கறிகள்**: கீரை வகைகள், முட்டைகோஸ், காலிஃப்ளவர்
• **வணிக பயிர்கள்**: பருத்தி, கரும்பு

🌱 **மண் மேம்பாட்டு முறைகள்**:
• மணல் மற்றும் கம்போஸ்ட் சேர்த்து வடிகால் மேம்படுத்தவும்
• ஆழமாக உழுது காற்று புகுமுகம் அதிகரிக்கவும்
• உயர்ந்த படுക்கை முறையில் பயிரிடவும்

எந்த பயிர் குறித்து விரிவாக தெரிந்து கொள்ள விரும்புகிறீர்கள்?"""
            },
            
            'hi-IN': {
                'sandy': """बलुई मिट्टी में खेती की सलाह:

🌾 **उपयुक्त फसलें**:
• **अनाज**: बाजरा, ज्वार, मक्का, धान (उच्च जल स्तर वाले क्षेत्रों में)
• **दलहन**: मूंग, उड़द, अरहर, चना
• **तिलहन**: मूंगफली, तिल, सरसों, सूरजमुखी
• **सब्जियां**: प्याज, लहसुन, गाजर, मूली, भिंडी
• **फल**: आम, अमरूद, नींबू, खजूर

🌱 **मिट्टी सुधार के तरीके**:
• गोबर की खाद और कंपोस्ट अधिक मात्रा में डालें
• साल में 2-3 बार जैविक खाद का प्रयोग करें
• हरी खाद की फसलें उगाएं (ढैंचा, सनई)
• पानी रोकने की क्षमता बढ़ाने के लिए वर्मी कंपोस्ट मिलाएं

💧 **पानी का प्रबंधन**:
• बार-बार लेकिन कम पानी दें
• ड्रिप इरिगेशन सबसे अच्छा है
• मल्चिंग करके नमी बनाए रखें

आप किस फसल के बारे में विस्तार से जानना चाहते हैं?""",
                
                'clay': """चिकनी मिट्टी में खेती की सलाह:

🌾 **उपयुक्त फसलें**:
• **अनाज**: धान, गेहूं, मक्का, ज्वार
• **दलहन**: अरहर, चना, मटर, सोयाबीन  
• **सब्जियां**: पत्तेदार सब्जियां, गोभी, फूलगोभी, बैंगन
• **नकदी फसलें**: कपास, गन्ना, हल्दी

🌱 **मिट्टी सुधार के तरीके**:
• रेत और कंपोस्ट मिलाकर जल निकासी सुधारें
• गहरी जुताई करके हवा का प्रवेश बढ़ाएं
• ऊंची क्यारी बनाकर खेती करें

किस फसल के बारे में विस्तार से जानना चाहते हैं?"""
            },
            
            'te-IN': {
                'sandy': """ఇసుక మట్టిలో వ్యవసాయ సలహా:

🌾 **తగిన పంటలు**:
• **ధాన్య పంటలు**: సజ్జలు, జొన్న, మొక్కజొన్న, రాగి
• **కాలధాన్యాలు**: పెసలు, మినుములు, కందులు, శనగలు
• **నూనె గింజలు**: వేరుశనగ, నువ్వులు, ఆవాలు, పొద్దుతిరుగుడు
• **కూరగాయలు**: ఉల్లిపాయలు, వెల్లుల్లి, క్యారెట్లు, ముల్లంగి
• **పండ్లు**: మామిడి, జాంబు, నిమ్మ, ఖర్జూరం

🌱 **మట్టి మెరుగుదల పద్ధతులు**:
• పశువుల ఎరువు మరియు కంపోస్ట్ ఎక్కువగా వేయండి
• సంవత్సరానికి 2-3 సార్లు సేంద్రీయ ఎరువులు వాడండి
• పచ్చిక ఎరువు పంటలు పండించండి (దంచ, సనపు)
• నీరు నిల్వ సామర్థ్యం పెంచడానికి వర్మీ కంపోస్ట్ కలపండి

💧 **నీటిపారుదల నిర్వహణ**:
• తరచుగా కానీ తక్కువ నీరు ఇవ్వండి
• డ్రిప్ ఇరిగేషన్ అత్యుత్తమం
• మల్చింగ్ చేసి తేమ కాపాడండి

ఏ పంట గురించి వివరంగా తెలుసుకోవాలనుకుంటున్నారు?"""
            }
        }
        
        # Determine soil type and return appropriate advice
        if any(keyword in text_lower for keyword in sandy_keywords):
            if language_code in soil_advice and 'sandy' in soil_advice[language_code]:
                return soil_advice[language_code]['sandy']
        elif any(keyword in text_lower for keyword in clay_keywords):
            if language_code in soil_advice and 'clay' in soil_advice[language_code]:
                return soil_advice[language_code]['clay']
        
        # Default soil advice if specific type not detected
        default_soil_advice = {
            'ta-IN': """மண்ணின் வகையை அறிந்து சரியான பயிர் தேர்வு செய்வது மிக முக்கியம்:

🌍 **மண் வகைகள்**:
• **மணல் மண்**: வடிகால் நல்லது, நீர் தேவை அதிகம்
• **களிமண்**: நீர் தேக்கும், வடிகால் மேம்பாடு தேவை  
• **கலப்பு மண்**: சிறந்த பயிர் வளர்ச்சிக்கு ஏற்றது

உங்கள் மண்ணின் வகை என்ன என்று குறிப்பிட்டால், அதற்கேற்ற பயிர் ஆலோசனை தருகிறேன்.""",

            'hi-IN': """मिट्टी का प्रकार जानकर सही फसल चुनना बहुत महत्वपूर्ण है:

🌍 **मिट्टी के प्रकार**:
• **बलुई मिट्टी**: जल निकासी अच्छी, पानी की अधिक आवश्यकता
• **चिकनी मिट्टी**: पानी रोकने वाली, जल निकासी सुधार की जरूरत
• **दोमट मिट्टी**: फसल उत्पादन के लिए सबसे अच्छी

आप अपनी मिट्टी का प्रकार बताएं तो मैं उसके अनुसार फसल की सलाह दूंगा।""",

            'te-IN': """మట్టి రకం తెలుసుకుని సరైన పంట ఎంపిక చేయడం చాలా ముఖ్యం:

🌍 **మట్టి రకాలు**:
• **ఇసుక మట్టి**: నీటి పారుదల మంచిది, నీరు ఎక్కువ కావాలి
• **బంక మట్టి**: నీరు నిల్వ చేస్తుంది, పారుదల మెరుగుదల కావాలి
• **లోమీ మట్టి**: పంట ఉత్పादనకు అత్యుత్తమం

మీ మట్టి రకం చెప్పండి, అందుకు తగిన పంట సలహా ఇస్తాను."""
        }
        
        return default_soil_advice.get(language_code, '')

    def _detect_language(self, text: str) -> str:
        """
        Auto-detect language from user input using Unicode script ranges and keywords.
        
        LANGUAGE DETECTION PROCESS:
        1. Analyze Unicode characters to identify script (Devanagari, Telugu, etc.)
        2. Use language-specific keywords for disambiguation
        3. Default to English if no Indian language detected
        4. Ensures response will be in the same language as input
        
        Args:
            text: User input text (typed or transcribed from speech)
            
        Returns:
            Language code (e.g., 'hi-IN', 'te-IN', 'en-US') for response generation
        """
        text_lower = text.lower()  # Convert to lowercase for consistent processing
        
        # Telugu language detection (Telugu script Unicode range)
        if any(ord(char) >= 0x0C00 and ord(char) <= 0x0C7F for char in text):
            return 'te-IN'  # Telugu (India)
        
        # Punjabi language detection (Gurmukhi script Unicode range)
        if any(ord(char) >= 0x0A00 and ord(char) <= 0x0A7F for char in text):
            return 'pa-IN'  # Punjabi (India)
        
        # Tamil language detection (Tamil script Unicode range)
        if any(ord(char) >= 0x0B80 and ord(char) <= 0x0BFF for char in text):
            return 'ta-IN'  # Tamil (India)
        
        # Bengali language detection (Bengali script Unicode range)
        if any(ord(char) >= 0x0980 and ord(char) <= 0x09FF for char in text):
            return 'bn-IN'  # Bengali (India)
        
        # Devanagari script detection (shared by Hindi and Marathi)
        if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):
            # Marathi-specific keywords to distinguish from Hindi
            marathi_words = ['काय', 'कसे', 'कुठे', 'कधी', 'शेती', 'पीक', 'खत']
            if any(word in text for word in marathi_words):
                return 'mr-IN'  # Marathi (India)
            return 'hi-IN'  # Hindi (India) - default for Devanagari
        
        # Gujarati language detection (Gujarati script Unicode range)
        if any(ord(char) >= 0x0A80 and ord(char) <= 0x0AFF for char in text):
            return 'gu-IN'  # Gujarati (India)
        
        # Kannada language detection (Kannada script Unicode range)
        if any(ord(char) >= 0x0C80 and ord(char) <= 0x0CFF for char in text):
            return 'kn-IN'  # Kannada (India)
        
        # Malayalam language detection (Malayalam script Unicode range)
        if any(ord(char) >= 0x0D00 and ord(char) <= 0x0D7F for char in text):
            return 'ml-IN'  # Malayalam (India)
        
        # No Spanish language support - removed as requested
        
        # Default to English if no other language detected
        return 'en-US'  # English (US)


class ChatbotService:
    """
    Main chatbot service orchestrating all components for agricultural assistance.
    
    COMPLETE CHATBOT RESPONSE GENERATION PROCESS:
    ===========================================
    
    1. INPUT PROCESSING:
       - Text Input: Direct text from user typing
       - Voice Input: Audio → Speech-to-Text → Text
    
    2. LANGUAGE DETECTION:
       - Auto-detect language from text/speech (Unicode + keywords)
       - Ensures response is in same native language as user input
    
    3. KNOWLEDGE MATCHING:
       - Search local agricultural knowledge base
       - Match user query with crop diseases, fertilizer advice, etc.
       - 4-pass matching: exact → keyword → topic → category
    
    4. RESPONSE GENERATION:
       - Generate text response in user's detected language
       - Convert to speech audio for voice users
       - Return both text and audio for complete experience
    
    5. OUTPUT DELIVERY:
       - Text users: Get text response in their native language
       - Voice users: Get both text + audio response in their language
    """
    
    def __init__(self):
        """Initialize all chatbot service components."""
        # Initialize Google Cloud Speech-to-Text service for voice input
        self.speech_to_text = SpeechToTextService()
        # Initialize Google Cloud Text-to-Speech service for voice output  
        self.text_to_speech = TextToSpeechService()
        # Initialize Dialogflow service (mainly for knowledge base access)
        self.dialogflow = DialogflowService()
    
    def process_text_message(self, text: str, session_id: str, language_code: str = 'auto') -> dict:
        """
        Process a text message and return response in user's native language.
        
        TEXT PROCESSING FLOW:
        1. Auto-detect language from input text (if language_code='auto')
        2. Search knowledge base for relevant agricultural information
        3. Generate response in the SAME language as user input
        4. Return text response with metadata
        
        Args:
            text: User input text (e.g., "धान की खेती कैसे करें?" or "How to grow rice?")
            session_id: Unique session identifier for tracking conversation
            language_code: Language code or 'auto' for automatic detection
            
        Returns:
            Dictionary containing:
            - text_response: Answer in user's native language
            - intent: Category of question (crop_diseases, fertilizer, etc.)
            - confidence: How confident the match was (0.0-1.0)
            - language_code: Detected/used language code
        """
        # Auto-detect language from user input if requested
        if language_code == 'auto':
            # Use advanced language detection to identify user's language
            language_code = self.dialogflow._detect_language(text)
        
        # Search knowledge base and generate response in detected language
        dialogflow_response = self.dialogflow.detect_intent(text, session_id, language_code)
        
        # Return complete response with metadata
        return {
            'text_response': dialogflow_response['fulfillment_text'],  # Answer in user's language
            'intent': dialogflow_response['intent'],                    # Question category
            'confidence': dialogflow_response['confidence'],            # Match confidence
            'language_code': language_code,                            # Language used
        }
    
    def process_voice_message(self, audio_data: bytes, session_id: str, language_code: str = 'auto') -> dict:
        """
        Process a voice message and return both text and audio response in user's language.
        
        VOICE PROCESSING FLOW:
        1. Convert user's speech to text (Speech-to-Text)
        2. Auto-detect language from transcribed text
        3. Search knowledge base for agricultural information
        4. Generate text response in user's native language
        5. Convert response back to speech (Text-to-Speech)
        6. Return both text and audio for complete experience
        
        Args:
            audio_data: Raw audio bytes from user's microphone
            session_id: Unique session identifier for tracking conversation
            language_code: Primary language hint or 'auto' for detection
            
        Returns:
            Dictionary containing:
            - transcribed_text: What the user said (in their language)
            - text_response: Written answer (in their language)
            - audio_response: Spoken answer (in their language)
            - intent: Category of question
            - confidence: Match confidence
            - language_code: Detected language
        """
        # Step 1: Convert user's speech to text
        transcribed_text = self.speech_to_text.transcribe_audio(audio_data, language_code)
        
        # Handle transcription failure
        if not transcribed_text:
            # Create error message in the expected language
            error_messages = {
                'hi-IN': "क्षमा करें, मैं आपकी आवाज़ समझ नहीं सका। कृपया फिर से कोशिश करें।",
                'te-IN': "క్షమించండి, నేను మీ వాయిస్ అర్థం చేసుకోలేకపోయాను. దయచేసి మళ్ళీ ప్రయత్నించండి.",
                'ta-IN': "மன்னிக்கவும், உங்கள் குரலை என்னால் புரிந்து கொள்ள முடியவில்லை. தயவுசெய்து மீண்டும் முயற்சிக்கவும்.",
                'en-US': "Sorry, I couldn't understand the audio. Please try again."
            }
            error_message = error_messages.get(language_code, error_messages['en-US'])
            
            return {
                'transcribed_text': '',                                    # Empty transcription
                'text_response': error_message,                           # Error in user's language
                'audio_response': self.text_to_speech.synthesize_speech(  # Spoken error message
                    error_message, language_code
                ),
                'intent': 'error',                                        # Error intent
                'confidence': 0.0,                                        # No confidence
                'language_code': language_code,                           # Language used
            }
        
        # Step 2: Auto-detect language from transcribed text if needed
        if language_code == 'auto':
            language_code = self.dialogflow._detect_language(transcribed_text)
        
        # Step 3: Process the transcribed text to get agricultural advice
        text_result = self.process_text_message(transcribed_text, session_id, language_code)
        
        # Step 4: Convert text response back to speech in user's language
        audio_response = self.text_to_speech.synthesize_speech(
            text_result['text_response'],   # Agricultural advice text
            language_code                   # User's native language
        )
        
        # Step 5: Return complete voice interaction result
        return {
            'transcribed_text': transcribed_text,          # What user said
            'text_response': text_result['text_response'], # Written agricultural advice
            'audio_response': audio_response,              # Spoken agricultural advice
            'intent': text_result['intent'],               # Question category
            'confidence': text_result['confidence'],       # Match confidence
            'language_code': language_code,                # User's language
        }