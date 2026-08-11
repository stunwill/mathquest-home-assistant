from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Mapping

LEGACY_SECRET = 'development-only-change-me'
SECRET_FILENAME = 'jwt-signing-secret'
MIN_SECRET_LENGTH = 32


class SecretConfigurationError(RuntimeError):
    """Raised when MathQuest cannot establish a safe JWT signing secret."""


def _is_valid(secret: str) -> bool:
    return len(secret) >= MIN_SECRET_LENGTH and secret != LEGACY_SECRET


def _persist_secret(path: Path, secret: str) -> None:
    temporary = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
            handle.write(secret)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        try:
            os.chmod(path, 0o600)
        except OSError:
            # Some mounted filesystems do not implement POSIX permissions.
            pass
    except OSError as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise SecretConfigurationError(
            f'Unable to persist the JWT signing secret at {path}'
        ) from exc


def load_signing_secret(
    data_dir: Path,
    environ: Mapping[str, str] | None = None,
) -> str:
    """Load an explicit secret or create and persist an installation secret."""
    environment = os.environ if environ is None else environ
    configured = environment.get('SECRET_KEY')
    if configured and configured != LEGACY_SECRET:
        if not _is_valid(configured):
            raise SecretConfigurationError(
                f'SECRET_KEY must contain at least {MIN_SECRET_LENGTH} characters'
            )
        return configured

    path = data_dir / SECRET_FILENAME
    try:
        if path.exists():
            persisted = path.read_text(encoding='utf-8').strip()
            if _is_valid(persisted):
                try:
                    os.chmod(path, 0o600)
                except OSError:
                    pass
                return persisted
            if persisted != LEGACY_SECRET:
                raise SecretConfigurationError(
                    f'The persisted JWT signing secret at {path} is invalid'
                )

        generated = secrets.token_urlsafe(48)
        _persist_secret(path, generated)
        persisted = path.read_text(encoding='utf-8').strip()
    except SecretConfigurationError:
        raise
    except OSError as exc:
        raise SecretConfigurationError(
            f'Unable to load the JWT signing secret from {path}'
        ) from exc

    if not _is_valid(persisted):
        raise SecretConfigurationError(
            f'JWT signing secret persistence verification failed at {path}'
        )
    return persisted
