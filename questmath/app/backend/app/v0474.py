from __future__ import annotations

from . import main as legacy, v0473

# A UX-only patch: retain the existing routes and learning model unchanged.
app = v0473.app
app.version = '0.47.4'
legacy.APP_VERSION = '0.47.4'
