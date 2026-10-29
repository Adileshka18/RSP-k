from backend.core import security as security_module
from backend.core.security import AuthService


def test_access_token_round_trip() -> None:
    service = AuthService(pepper="test-pepper", token_secret="test-secret")

    token = service.create_access_token(42, token_version=3, expires_in_seconds=3600)

    token_data = service.verify_access_token(token)

    assert token_data.user_id == 42
    assert token_data.token_version == 3
    assert token_data.expires_at > token_data.issued_at


def test_access_token_rejects_tampering() -> None:
    service = AuthService(pepper="test-pepper", token_secret="test-secret")

    token = service.create_access_token(42, expires_in_seconds=3600)
    parts = token.split(".")
    tampered_payload = parts[1][::-1]
    tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

    try:
        service.verify_access_token(tampered_token)
    except ValueError as exc:
        assert "токена" in str(exc)
    else:  # pragma: no cover - defensive branch
        raise AssertionError("Подделанный токен должен быть отклонен")


def test_access_token_expires(monkeypatch) -> None:
    service = AuthService(pepper="test-pepper", token_secret="test-secret")

    monkeypatch.setattr(security_module.time, "time", lambda: 1_700_000_000)
    token = service.create_access_token(42, expires_in_seconds=60)

    monkeypatch.setattr(security_module.time, "time", lambda: 1_700_000_061)

    try:
        service.verify_access_token(token)
    except ValueError as exc:
        assert "истек" in str(exc)
    else:  # pragma: no cover - defensive branch
        raise AssertionError("Просроченный токен должен быть отклонен")


def test_legacy_password_hash_still_verifies() -> None:
    service = AuthService(pepper="test-pepper", token_secret="test-secret")
    legacy_hash = service._legacy_password_hash("secret123")

    assert service.verify_password("secret123", legacy_hash)
