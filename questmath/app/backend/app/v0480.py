from __future__ import annotations

from . import main as legacy, v0476

# Persisted adaptive follow-through release.
app = v0476.app
app.version = '0.48.0'
legacy.APP_VERSION = '0.48.0'
