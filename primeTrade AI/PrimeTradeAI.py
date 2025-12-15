import os
import sys
import subprocess
import time

def ensure_dependencies():
    try:
        import fastapi  # noqa: F401
        import uvicorn  # noqa: F401
        import sqlalchemy  # noqa: F401
        import passlib  # noqa: F401
        import jose  # noqa: F401
    except Exception:
        req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])

def run_server():
    import uvicorn
    from app.main import app
    print("Starting PrimeTrade AI on http://127.0.0.1:8000/")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    ensure_dependencies()
    run_server()
