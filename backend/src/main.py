from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.db.session import init_db, close_db

from src.router.user import router as user_router
from src.router.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initializing  database
    await init_db()
    
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

app.include_router(auth_router, prefix=f"{settings.API_PREFIX}/auth", tags=["auth"])
app.include_router(user_router, prefix=f"{settings.API_PREFIX}/user", tags=["users"])
