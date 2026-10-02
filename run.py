"""Start the TraceInbox development web server with ``python run.py``."""
from app.main import app  # noqa: F401
from app import config

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=not config.PUBLIC_DEMO)
