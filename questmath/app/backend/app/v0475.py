from __future__ import annotations

from . import main as legacy, v0474

# Parent Dashboard resilience release: frontend fix is carried by the bundled UI.
# Retain the existing backend routes and learning model unchanged.
app = v0474.app
app.version = '0.47.5'
legacy.APP_VERSION = '0.47.5'
