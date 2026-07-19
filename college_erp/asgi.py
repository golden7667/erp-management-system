import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_erp.settings')

# Initialize Django ASGI application first to load everything
django_asgi_app = get_asgi_application()

# Import FastAPI app only after Django ASGI initialization
from departments.fastapi_app import fastapi_app

async def application(scope, receive, send):
    if (scope['type'] in ('http', 'websocket')) and scope['path'].startswith('/fastapi'):
        # Forward requests starting with /fastapi to FastAPI
        await fastapi_app(scope, receive, send)
    else:
        # Default all other routes to Django
        await django_asgi_app(scope, receive, send)
