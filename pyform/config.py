from pathlib import Path
from starlette.templating import Jinja2Templates

## This is the configuration file for the pyform project.
## It sets up the base path, static files path, and templates path.

BASE_PATH = Path(__file__).resolve().parent
STATIC_PATH = BASE_PATH / "static"
TEMPLATES_PATH = BASE_PATH / "templates"

#Network configuration
NETWORK_CONFIG = {
    "host": "0.0.0.0",
    "port": 9093,
    "debug": True,
}

# Template configuration

# Template settings
TEMPLATES = Jinja2Templates(directory=TEMPLATES_PATH)

