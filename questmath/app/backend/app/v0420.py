from __future__ import annotations

from fastapi import Depends

from . import main as legacy
from . import v0120, v0410

app = v0410.app
app.version = '0.42.0'
legacy.APP_VERSION = '0.42.0'


@app.get('/api/v0420/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.42.0',
        'student_destination_navigation': True,
        'learner_safe_guidance': True,
        'ready_to_start_semantics': True,
        'student_progress_grouping': True,
        'learning_engine_unchanged': True,
        'inherits_v0410': True,
    }


v0120._move_spa_fallback_to_end()
