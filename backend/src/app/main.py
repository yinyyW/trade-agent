from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.lifespan import lifespan
from app.home.router import router as home_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trade Agent",
    description="金融智能投研 Agent 后端服务",
    version="0.1.0",
    lifespan=lifespan,
)


# =========================================================
# Middleware
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Routers
# =========================================================

app.include_router(home_router)


# =========================================================
# System APIs
# =========================================================


@app.get(
    "/",
    tags=["系统"],
)
async def root():
    return {
        "code": 0,
        "message": "Trade Agent API",
    }


@app.get(
    "/health",
    tags=["系统"],
)
async def health():
    return {
        "code": 0,
        "message": "ok",
    }