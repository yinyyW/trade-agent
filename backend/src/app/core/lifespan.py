from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.runtime.runtime import ApplicationRuntime

@asynccontextmanager
async def lifespan(app: FastAPI):

    runtime = ApplicationRuntime()

    await runtime.startup()

    app.state.runtime = runtime

    try:
        yield

    finally:
        await runtime.shutdown()