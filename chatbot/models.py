from django.db import models
from django.utils import timezone


class KnowledgeBase(models.Model):
    """Core agricultural knowledge stored in the database."""
    
    CATEGORY_CHOICES = [
        ('crop_diseases', 'Crop Diseases'),
        ('pest_identification', 'Pest Identification'),
        ('fertilizer_recommendations', 'Fertilizer Recommendations'),
        ('weather_advice', 'Weather Advice'),
        ('soil_health', 'Soil Health'),
        ('general', 'General Agriculture'),
    ]
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    topic = models.CharField(max_length=200)
    question_patterns = models.TextField(help_text="Common question patterns, separated by newlines")
    answer = models.TextField()
    language_code = models.CharField(max_length=10, default='en-US')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'topic']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['language_code']),
        ]
    
    def __str__(self):
        return f"{self.category}: {self.topic}"


class ChatSession(models.Model):
    """Track user chat sessions."""
    
    session_id = models.CharField(max_length=100, unique=True)
    language_code = models.CharField(max_length=10, default='en-US')
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Session {self.session_id} ({self.language_code})"


class ChatMessage(models.Model):
    """Store chat messages for history and analytics."""
    
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    audio_file = models.FileField(upload_to='audio/', null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True, help_text="Response time in seconds")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."