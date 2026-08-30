from __future__ import annotations

from . import main as legacy
from . import v0350

app = v0350.app
app.version = '0.35.1'
legacy.APP_VERSION = '0.35.1'
