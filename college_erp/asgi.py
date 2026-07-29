import os
from django.core.asgi import get_asgi_application

from fastapi import FastAPI

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_erp.settings')

# Initialize Django ASGI application first to load everything
django_asgi_app = get_asgi_application()

# Import FastAPI app only after Django ASGI initialization
from departments.fastapi_app import fastapi_app

# Main ASGI application callable
async def application(scope, receive, send):
    if (scope['type'] in ('http', 'websocket')) and scope['path'].startswith('/fastapi'):
        await fastapi_app(scope, receive, send)
    else:
        await django_asgi_app(scope, receive, send)

app = application

