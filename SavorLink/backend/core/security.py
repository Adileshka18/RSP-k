from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass

from backend.core.config import get_auth_token_secret, get_auth_token_ttl_seconds

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
except ImportError:  # pragma: no cover - optional dependency
    PasswordHasher = None
    VerifyMismatchError = None


@dataclass(frozen=True)
class AccessTokenData:
    user_id: int
    token_version: int
    issued_at: int
    expires_at: int
    token_id: str


class AuthService:
    """
    Вспомогательный сервис для MVP-аутентификации.
    Для production это нужно заменить на passlib/bcrypt/argon2 и полноценные сессии.
    """

    token_version = "sl2"

    def __init__(self, pepper: str | None = None, token_secret: str | None = None) -> None:
        self.pepper = pepper or os.getenv("PASSWORD_PEPPER", "dev-pepper")
        self.token_secret = token_secret or get_auth_token_secret()
        self._argon2_hasher = PasswordHasher(
            time_cost=3,
            memory_cost=64 * 1024,
            parallelism=2,
        ) if PasswordHasher is not None else None

    def hash_password(self, password: str) -> str:
        if self._argon2_hasher is not None:
            return self._argon2_hasher.hash(password)

        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            (self.pepper + password).encode("utf-8"),
            salt,
            260_000,
        )
        return f"pbkdf2_sha256$260000${self._encode_segment(salt)}${self._encode_segment(digest)}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        if password_hash.startswith("$argon2") and self._argon2_hasher is not None:
            try:
                return bool(self._argon2_hasher.verify(password_hash, password))
            except VerifyMismatchError:
                return False
            except Exception:  # pragma: no cover - defensive fallback
                return False

        if password_hash.startswith("pbkdf2_sha256$"):
            try:
                algorithm, rounds, salt_part, digest_part = password_hash.split("$", 3)
            except ValueError:
                return False

            if algorithm != "pbkdf2_sha256":
                return False

            try:
                iterations = int(rounds)
                salt = self._decode_segment(salt_part)
                expected_digest = self._decode_segment(digest_part)
            except (ValueError, TypeError):
                return False

            actual_digest = hashlib.pbkdf2_hmac(
                "sha256",
                (self.pepper + password).encode("utf-8"),
                salt,
                iterations,
            )
            return hmac.compare_digest(actual_digest, expected_digest)

        legacy_digest = self._legacy_password_hash(password)
        return hmac.compare_digest(legacy_digest, password_hash)

    def create_access_token(
        self,
        user_id: int,
        *,
        token_version: int = 0,
        expires_in_seconds: int | None = None,
    ) -> str:
        issued_at = int(time.time())
        expires_in = expires_in_seconds or get_auth_token_ttl_seconds()
        payload = {
            "sub": user_id,
            "tv": token_version,
            "iat": issued_at,
            "exp": issued_at + expires_in,
            "jti": secrets.token_urlsafe(16),
        }
        payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        payload_part = self._encode_segment(payload_json.encode("utf-8"))
        signature_part = self._sign(payload_part.encode("ascii"))
        return f"{self.token_version}.{payload_part}.{signature_part}"

    def verify_access_token(self, token: str) -> AccessTokenData:
        parts = token.split(".")
        if len(parts) != 3 or parts[0] != self.token_version:
            raise ValueError("Неверный формат токена")

        payload_part = parts[1]
        signature_part = parts[2]
        expected_signature = self._sign(payload_part.encode("ascii"))
        if not hmac.compare_digest(expected_signature, signature_part):
            raise ValueError("Недействительная подпись токена")

        payload_raw = self._decode_segment(payload_part)
        payload = json.loads(payload_raw.decode("utf-8"))
        user_id = self._require_int(payload, "sub", "В токене указан некорректный ID пользователя")
        token_version = self._require_int(payload, "tv", "В токене указана некорректная версия токена")
        issued_at = self._require_int(payload, "iat", "В токене указано некорректное время выдачи")
        expires_at = self._require_int(payload, "exp", "В токене указано некорректное время истечения")
        token_id = payload.get("jti")
        if not isinstance(token_id, str) or not token_id:
            raise ValueError("В токене отсутствует идентификатор")

        if expires_at <= issued_at:
            raise ValueError("В токене указано некорректное время истечения")

        if int(time.time()) >= expires_at:
            raise ValueError("Срок действия токена истек")

        return AccessTokenData(
            user_id=user_id,
            token_version=token_version,
            issued_at=issued_at,
            expires_at=expires_at,
            token_id=token_id,
        )

    def _sign(self, message: bytes) -> str:
        digest = hmac.new(self.token_secret.encode("utf-8"), message, hashlib.sha256).digest()
        return self._encode_segment(digest)

    def _legacy_password_hash(self, password: str) -> str:
        return hashlib.sha256((self.pepper + password).encode("utf-8")).hexdigest()

    @staticmethod
    def _require_int(payload: dict[str, object], key: str, message: str) -> int:
        value = payload.get(key)
        if isinstance(value, bool):
            raise ValueError(message)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        raise ValueError(message)

    @staticmethod
    def _encode_segment(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    @staticmethod
    def _decode_segment(segment: str) -> bytes:
        padding = "=" * (-len(segment) % 4)
        return base64.urlsafe_b64decode(segment + padding)
