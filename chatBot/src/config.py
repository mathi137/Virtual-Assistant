import os

# Get webhook base URL from environment (for production, should be set to the public URL)
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8001")

# Backend API URLs
BACKEND_CHAT_API_URL = "http://backend:8000/api/v1/agent/chat/"
BACKEND_AGENTS_API_URL = "http://backend:8000/api/v1/agent/"

