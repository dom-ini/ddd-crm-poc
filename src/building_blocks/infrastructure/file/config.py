import os
from pathlib import Path

_DEFAULT_PATH = Path.home()
ROOT_FILES_PATH = Path(os.getenv("ROOT_FILES_PATH") or str(_DEFAULT_PATH))
