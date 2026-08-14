from __future__ import annotations

from fastapi import Depends

from . import main as legacy
from . import v0120, v0200

app = v0200.app
app.version = legacy.APP_VERSION


@app.get('/api/v0210/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': legacy.APP_VERSION,
        'interactive_maths_lab': True,
        'react_owned_lab': True,
        'available_from_every_question': True,
        'models': [
            'fractions', 'percentages', 'number_line', 'place_value',
            'arrays', 'clock', 'grid', 'measurement',
        ],
        'responsive_layouts': ['desktop', 'mobile', 'home_assistant'],
        'inherits_v0200': True,
    }


v0120._move_spa_fallback_to_end()
