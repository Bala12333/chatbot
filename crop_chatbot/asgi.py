"""
ASGI config for crop_chatbot project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crop_chatbot.settings')

application = get_asgi_application()