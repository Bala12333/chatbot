"""
Tests for the chatbot application.
"""

import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import KnowledgeBase, ChatSession, ChatMessage


class ChatbotModelTests(TestCase):
    """Test cases for chatbot models."""
    
    def setUp(self):
        self.knowledge_entry = KnowledgeBase.objects.create(
            category='crop_diseases',
            topic='Test Disease',
            question_patterns='test disease\ndisease test',
            answer='This is a test answer for disease.',
            language_code='en-US'
        )
        
        self.session = ChatSession.objects.create(
            session_id='test-session-123',
            language_code='en-US'
        )
    
    def test_knowledge_base_creation(self):
        """Test knowledge base entry creation."""
        self.assertEqual(self.knowledge_entry.topic, 'Test Disease')
        self.assertEqual(self.knowledge_entry.category, 'crop_diseases')
        self.assertEqual(self.knowledge_entry.language_code, 'en-US')
    
    def test_chat_session_creation(self):
        """Test chat session creation."""
        self.assertEqual(self.session.session_id, 'test-session-123')
        self.assertEqual(self.session.language_code, 'en-US')
    
    def test_chat_message_creation(self):
        """Test chat message creation."""
        message = ChatMessage.objects.create(
            session=self.session,
            message_type='user',
            content='Test message'
        )
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(message.message_type, 'user')
        self.assertEqual(message.session, self.session)


class ChatbotViewTests(TestCase):
    """Test cases for chatbot views."""
    
    def setUp(self):
        self.client = Client()
        
        # Create test knowledge base entry
        KnowledgeBase.objects.create(
            category='crop_diseases',
            topic='Tomato Blight',
            question_patterns='tomato blight\ntomato disease',
            answer='Tomato blight treatment information.',
            language_code='en-US'
        )
    
    def test_index_view(self):
        """Test the main index view."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Crop Crystalline Chatbot')
    
    def test_chat_api_view(self):
        """Test the chat API endpoint."""
        data = {
            'message': 'tomato blight',
            'language_code': 'en-US'
        }
        response = self.client.post(
            '/api/chat/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertIn('response', response_data)
        self.assertIn('session_id', response_data)
    
    def test_chat_api_empty_message(self):
        """Test chat API with empty message."""
        data = {
            'message': '',
            'language_code': 'en-US'
        }
        response = self.client.post(
            '/api/chat/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_supported_languages_view(self):
        """Test the supported languages endpoint."""
        response = self.client.get('/api/languages/')
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertIn('languages', response_data)
        self.assertIsInstance(response_data['languages'], list)
    
    def test_health_check_view(self):
        """Test the health check endpoint."""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'healthy')
    
    def test_chat_history_view(self):
        """Test the chat history endpoint."""
        # Create a session with messages
        session = ChatSession.objects.create(
            session_id='test-history-session',
            language_code='en-US'
        )
        
        ChatMessage.objects.create(
            session=session,
            message_type='user',
            content='Test user message'
        )
        
        ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content='Test bot response'
        )
        
        response = self.client.get(f'/api/history/{session.session_id}/')
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertIn('history', response_data)
        self.assertEqual(len(response_data['history']), 2)
    
    def test_chat_history_not_found(self):
        """Test chat history for non-existent session."""
        response = self.client.get('/api/history/non-existent-session/')
        self.assertEqual(response.status_code, 404)


class ChatbotServiceTests(TestCase):
    """Test cases for chatbot services."""
    
    def setUp(self):
        # Create test knowledge base entries
        KnowledgeBase.objects.create(
            category='crop_diseases',
            topic='Tomato Blight',
            question_patterns='tomato blight\ntomato disease',
            answer='Tomato blight treatment information.',
            language_code='en-US'
        )
        
        KnowledgeBase.objects.create(
            category='pest_identification',
            topic='Aphids',
            question_patterns='aphids\ngreen bugs',
            answer='Aphid control information.',
            language_code='en-US'
        )
    
    def test_knowledge_base_search(self):
        """Test knowledge base search functionality."""
        from .services import DialogflowService
        
        dialogflow_service = DialogflowService()
        
        # Test matching question
        result = dialogflow_service._fallback_to_knowledge_base('tomato blight', 'en-US')
        self.assertEqual(result['intent'], 'ai_enhanced_response')
        self.assertIn('blight', result['fulfillment_text'].lower())
        
        # Test non-matching question
        result = dialogflow_service._fallback_to_knowledge_base('random question', 'en-US')
        self.assertEqual(result['intent'], 'ai_enhanced_response')
    
    def test_default_response_languages(self):
        """Test default responses in different languages."""
        from .services import DialogflowService
        
        dialogflow_service = DialogflowService()
        
        # Test English default response
        en_response = dialogflow_service._get_default_response('en-US')
        self.assertIn('farming questions', en_response)
        
        # Test Spanish default response
        es_response = dialogflow_service._get_default_response('es-ES')
        self.assertIn('agricultura', es_response)
        
        # Test fallback to English for unsupported language
        fallback_response = dialogflow_service._get_default_response('unsupported-lang')
        self.assertIn('farming questions', fallback_response)