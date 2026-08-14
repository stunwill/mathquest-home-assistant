from __future__ import annotations

import logging
import stat

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0160
from app.auth_security import LoginRateLimiter
from app.security import (
    HA_SERVICE_TOKEN_FILENAME,
    LEGACY_SECRET,
    SECRET_FILENAME,
    SecretConfigurationError,
    load_ha_service_token,
    load_signing_secret,
)


def test_new_secret_is_generated_and_persisted(tmp_path):
    secret = load_signing_secret(tmp_path, {})
    path = tmp_path / SECRET_FILENAME
    assert secret != LEGACY_SECRET
    assert len(secret) >= 32
    assert path.read_text(encoding='utf-8').strip() == secret
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_secret_remains_stable_across_simulated_restarts(tmp_path):
    first = load_signing_secret(tmp_path, {})
    second = load_signing_secret(tmp_path, {})
    assert second == first


def test_ha_service_token_remains_stable_across_simulated_restarts(tmp_path):
    first = load_ha_service_token(tmp_path, {})
    second = load_ha_service_token(tmp_path, {})
    path = tmp_path / HA_SERVICE_TOKEN_FILENAME
    assert second == first
    assert len(first) >= 32
    assert path.read_text(encoding='utf-8').strip() == first
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_explicit_environment_secret_is_honoured(tmp_path):
    explicit = 'operator-supplied-secret-value-that-is-long-enough'
    assert load_signing_secret(tmp_path, {'SECRET_KEY': explicit}) == explicit
    assert not (tmp_path / SECRET_FILENAME).exists()


def test_legacy_environment_value_is_replaced(tmp_path):
    secret = load_signing_secret(tmp_path, {'SECRET_KEY': LEGACY_SECRET})
    assert secret != LEGACY_SECRET
    assert (tmp_path / SECRET_FILENAME).read_text(encoding='utf-8').strip() == secret


def test_legacy_persisted_value_is_rotated(tmp_path):
    path = tmp_path / SECRET_FILENAME
    path.write_text(LEGACY_SECRET, encoding='utf-8')
    secret = load_signing_secret(tmp_path, {})
    assert secret != LEGACY_SECRET
    assert path.read_text(encoding='utf-8').strip() == secret


def test_invalid_explicit_secret_fails_closed(tmp_path):
    with pytest.raises(SecretConfigurationError, match='at least'):
        load_signing_secret(tmp_path, {'SECRET_KEY': 'too-short'})


def _client_with_user(monkeypatch):
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    user = legacy.User(
        username='student',
        password_hash=legacy.pwd.hash('correct-password'),
        role='student',
        display_name='Test Learner',
    )
    session.add(user)
    session.commit()

    def test_db():
        yield session

    v0160.app.dependency_overrides[legacy.db] = test_db
    limiter = LoginRateLimiter(failure_limit=5, window_seconds=300, max_entries=100)
    monkeypatch.setattr(legacy, 'login_rate_limiter', limiter)
    return TestClient(v0160.app), session, limiter


def test_successful_login_returns_token_without_exposing_secret(monkeypatch, caplog):
    client, session, _ = _client_with_user(monkeypatch)
    caplog.set_level(logging.INFO, logger='mathquest.security')
    response = client.post('/api/auth/login', data={'username': 'student', 'password': 'correct-password'})
    assert response.status_code == 200
    assert response.json()['access_token']
    assert legacy.SECRET_KEY not in response.text
    health = client.get('/api/health')
    assert health.status_code == 200
    assert legacy.SECRET_KEY not in health.text
    assert legacy.SECRET_KEY not in caplog.text
    v0160.app.dependency_overrides.clear()
    session.close()


def test_repeated_failures_are_rate_limited(monkeypatch, caplog):
    client, session, limiter = _client_with_user(monkeypatch)
    caplog.set_level(logging.WARNING, logger='mathquest.security')
    for _ in range(limiter.failure_limit):
        response = client.post('/api/auth/login', data={'username': 'student', 'password': 'wrong-password'})
        assert response.status_code == 401
        assert response.json()['detail'] == 'Invalid username or password'
    blocked = client.post('/api/auth/login', data={'username': 'student', 'password': 'wrong-password'})
    assert blocked.status_code == 429
    assert int(blocked.headers['Retry-After']) > 0
    assert 'wrong-password' not in caplog.text
    assert legacy.SECRET_KEY not in caplog.text
    v0160.app.dependency_overrides.clear()
    session.close()


def test_unknown_username_uses_same_authentication_error(monkeypatch):
    client, session, _ = _client_with_user(monkeypatch)
    response = client.post('/api/auth/login', data={'username': 'unknown', 'password': 'wrong-password'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid username or password'
    v0160.app.dependency_overrides.clear()
    session.close()


def test_retry_window_and_successful_recovery(monkeypatch):
    client, session, _ = _client_with_user(monkeypatch)
    clock = {'now': 100.0}
    monkeypatch.setattr('app.auth_security.time.monotonic', lambda: clock['now'])
    limiter = LoginRateLimiter(failure_limit=2, window_seconds=10, max_entries=100)
    monkeypatch.setattr(legacy, 'login_rate_limiter', limiter)
    for _ in range(2):
        assert client.post('/api/auth/login', data={'username': 'student', 'password': 'wrong'}).status_code == 401
    blocked = client.post('/api/auth/login', data={'username': 'student', 'password': 'correct-password'})
    assert blocked.status_code == 429
    assert blocked.headers['Retry-After'] == '10'
    clock['now'] = 111.0
    recovered = client.post('/api/auth/login', data={'username': 'student', 'password': 'correct-password'})
    assert recovered.status_code == 200
    assert limiter.state_size == 0
    v0160.app.dependency_overrides.clear()
    session.close()


def test_rate_limit_state_is_bounded():
    limiter = LoginRateLimiter(failure_limit=5, window_seconds=300, max_entries=3)
    for index in range(10):
        limiter.record_failure((f'client-{index}', 'student'), now=float(index))
    assert limiter.state_size <= 3
