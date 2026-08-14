from __future__ import annotations

from fastapi import Depends

from . import main as legacy
from . import v0120, v0210, v090

app = v0210.app
app.version = legacy.APP_VERSION


@app.get('/api/v0220/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': legacy.APP_VERSION,
        'story_adventures_2': True,
        'themes': list(v090.ADVENTURES),
        'coherent_missions': True,
        'adaptive_learning_goals': True,
        'shared_mission_data': True,
        'chapter_progress': True,
        'applied_multi_step_problems': True,
        'mission_outcomes': True,
        'inherits_v0210': True,
    }


v0120._move_spa_fallback_to_end()
