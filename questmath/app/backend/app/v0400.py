from __future__ import annotations

from fastapi import Depends

from . import main as legacy
from . import v0120, v0390

app = v0390.app
app.version = '0.40.0'
legacy.APP_VERSION = '0.40.0'


@app.get('/api/v0400/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.40.0',
        'student_mobile_home': True,
        'continue_learning_priority': True,
        'compact_mobile_adventure_selection': True,
        'progressive_worksheet_history': True,
        'mobile_student_navigation': True,
        'responsive_week_navigation': True,
        'learning_engine_unchanged': True,
        'inherits_v0390': True,
    }


v0120._move_spa_fallback_to_end()
