from __future__ import annotations

from . import main as legacy, v0475

# Worksheet history and review release: backend APIs remain compatible.
app = v0475.app
app.version = '0.47.6'
legacy.APP_VERSION = '0.47.6'
