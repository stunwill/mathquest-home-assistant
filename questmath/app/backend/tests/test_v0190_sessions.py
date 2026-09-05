from fastapi.testclient import TestClient

from app import main, v0190


def login(client):
    response = client.post('/api/auth/login', data={'username': 'student', 'password': 'ChangeMeStudent!'})
    assert response.status_code == 200
    return {'Authorization': f"Bearer {response.json()['access_token']}"}


def test_timed_session_has_duration_and_bounded_question_count():
    with TestClient(v0190.app) as client:
        response = client.post('/api/sessions/new', headers=login(client), json={
            'kind': 'practice', 'minutes': 5, 'topic': 'number_algebra'
        })
    assert response.status_code == 200
    data = response.json()
    assert data['session_kind'] == 'timed'
    assert data['target_minutes'] == 5
    assert data['total'] == 6


def test_diagnostic_covers_level_five_and_level_six_only():
    with TestClient(v0190.app) as client:
        headers = login(client)
        created = client.post('/api/sessions/new', headers=headers, json={
            'kind': 'diagnostic', 'minutes': 15, 'topic': 'number_algebra'
        })
        result = client.get('/api/diagnostic/latest', headers=headers)
        capabilities = client.get('/api/v0190/capabilities', headers=headers)
    assert created.status_code == 200
    assert created.json()['total'] == 6
    assert [question['level'] for question in created.json()['questions']] == [5, 5, 5, 6, 6, 6]
    assert result.status_code == 200
    assert [item['level'] for item in result.json()['levels']] == [5, 6]
    assert capabilities.status_code == 200
    assert capabilities.json()['diagnostic_levels'] == [5, 6]


def test_existing_database_migration_adds_session_columns():
    main.migrate_database()
    with main.sqlite3.connect(main.DB_PATH) as connection:
        columns = {row[1] for row in connection.execute('PRAGMA table_info(worksheets)')}
    assert {'session_kind', 'target_minutes'} <= columns
