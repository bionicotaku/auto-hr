from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import AppError, register_exception_handlers


def test_business_exception_uses_unified_error_payload() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise AppError("boom", {"scope": "test"})

    client = TestClient(app)
    response = client.get("/boom")

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "app_error",
            "message": "boom",
            "details": {"scope": "test"},
        }
    }


def test_unexpected_exception_does_not_leak_traceback() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/crash")
    def crash() -> None:
        raise RuntimeError("sensitive traceback content")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/crash")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "internal_error",
            "message": "Internal server error.",
            "details": {},
        }
    }
    assert "traceback" not in response.text.lower()
    assert "sensitive traceback content" not in response.text
