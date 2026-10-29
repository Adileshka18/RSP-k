from __future__ import annotations

import json
import os
from urllib.error import URLError
from urllib.request import urlopen

import pytest


BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8002").rstrip("/")


def _request(path: str) -> tuple[int, str, str]:
    url = f"{BASE_URL}{path}"
    try:
        with urlopen(url, timeout=5) as response:
            body = response.read().decode("utf-8")
            content_type = response.headers.get_content_type()
            return response.status, body, content_type
    except URLError as exc:  # pragma: no cover - only used when the stack is down
        pytest.skip(f"API is not reachable at {BASE_URL}: {exc}")


def test_root_endpoint_is_alive() -> None:
    status, body, content_type = _request("/")

    assert status == 200
    assert content_type == "application/json"
    payload = json.loads(body)
    assert payload["message"] == "Добро пожаловать в API SavorLink"


def test_openapi_and_products_categories_are_available() -> None:
    status, body, content_type = _request("/openapi.json")

    assert status == 200
    assert content_type == "application/json"
    openapi = json.loads(body)
    assert openapi["info"]["title"] == "SavorLink API"

    status, body, content_type = _request("/products/categories")
    assert status == 200
    assert content_type == "application/json"
    categories = json.loads(body)
    assert isinstance(categories, list)
