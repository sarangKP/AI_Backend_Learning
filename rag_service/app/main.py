from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: anything that needs to happen before serving requests
    yield
    # Shutdown: cleanup (close connections, flush buffers, etc.)


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tightened in Day 2
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
