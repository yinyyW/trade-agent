# dependencies.py

from fastapi import Request

from app.runtime.runtime import ApplicationRuntime


def get_runtime(request: Request) -> ApplicationRuntime:
    return request.app.state.runtime