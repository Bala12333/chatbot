from django.contrib import admin
from .models import KnowledgeBase, ChatSession, ChatMessage


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['topic', 'category', 'language_code', 'created_at']
    list_filter = ['category', 'language_code', 'created_at']
    search_fields = ['topic', 'question_patterns', 'answer']
    ordering = ['category', 'topic']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'language_code', 'created_at', 'last_activity']
    list_filter = ['language_code', 'created_at']
    search_fields = ['session_id']
    readonly_fields = ['created_at', 'last_activity']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'response_time', 'timestamp']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['content']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'