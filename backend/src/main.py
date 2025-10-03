from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.db.session import init_db, close_db, populate_db

from src.routers.user import router as user_router
from src.routers.auth import router as auth_router
from src.routers.agent import router as agent_router
from src.routers.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initializing  database
    await init_db()
    # Populate database with initial data
    await populate_db()
    
    yield

    # Closing database
    await close_db()


app = FastAPI(
    lifespan=lifespan,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # <-- all domains
    allow_credentials=True,     # <-- cookies, auth headers
    allow_methods=["*"],        # <-- GET, POST, PUT, DELETE, PATCH, etc.
    allow_headers=["*"],        # <-- any headers
)

app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth", tags=["Auth"])
app.include_router(user_router, prefix=f"{settings.API_PREFIX}/user", tags=["User"])
app.include_router(agent_router, prefix=f"{settings.API_PREFIX}/agent", tags=["Agent"])
app.include_router(chat_router, prefix=f"{settings.API_PREFIX}/chat", tags=["Chat"])
