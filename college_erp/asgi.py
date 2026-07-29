import os
from django.core.asgi import get_asgi_application

from fastapi import FastAPI

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_erp.settings')

# Initialize Django ASGI application first to load everything
django_asgi_app = get_asgi_application()

# Import FastAPI app only after Django ASGI initialization
from departments.fastapi_app import fastapi_app

# Create root FastAPI app so Vercel CLI detects it as a FastAPI entrypoint
app = FastAPI(title="Smart College ERP")

# Mount FastAPI sub-application under /fastapi
app.mount("/fastapi", fastapi_app)

# Mount Django ASGI application to handle all other routes
app.mount("/", django_asgi_app)

application = app
