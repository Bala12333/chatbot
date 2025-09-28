"""
URL patterns for the chatbot application.
"""

from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Main interface
    path('', views.index, name='index'),
    path('conversation-mode/', views.conversation_mode, name='conversation_mode'),
    
    # API endpoints
    path('api/chat/', views.ChatAPIView.as_view(), name='chat_api'),
    path('api/voice-chat/', views.VoiceChatAPIView.as_view(), name='voice_chat_api'),
    path('api/speech-to-text/', views.SpeechToTextAPIView.as_view(), name='speech_to_text_api'),
    path('api/history/<str:session_id>/', views.chat_history, name='chat_history'),
    path('api/languages/', views.supported_languages, name='supported_languages'),
    path('api/health/', views.health_check, name='health_check'),
]