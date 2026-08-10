from __future__ import annotations

from fastapi import Depends

from . import main as legacy
from . import v0130
from . import v0110, v0120

app = legacy.app
app.version = '0.14.0'


@app.get('/api/v0140/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.14.0',
        'date_scoped_today_quest': True,
        'previous_unfinished_separated': True,
        'multiple_worksheets_per_day': True,
        'completed_worksheet_review': True,
        'home_assistant_quest_today_state': True,
        'home_assistant_previous_unfinished_count': True,
        'visual_hints': True,
    }


def _move_spa_fallback_to_end() -> None:
    routes = app.router.routes
    for index, route in enumerate(list(routes)):
        if getattr(route, 'path', None) == '/{path:path}':
            routes.append(routes.pop(index))
            break


_move_spa_fallback_to_end()
