from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.router.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # <-- all domains
    allow_credentials=True,     # <-- cookies, auth headers
    allow_methods=["*"],        # <-- GET, POST, PUT, DELETE, PATCH, etc.
    allow_headers=["*"],        # <-- any headers
)

app.include_router(user_router, prefix="/user", tags=["users"])
