"""Vercel entrypoint for backend service.

Ensures the 'backend' package namespace is available and resolves to this directory,
guaranteeing that all absolute imports ('from backend.app.*') succeed even when
Vercel isolates the build to 'backend/' as the service root.
"""
import sys
import types
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent

# If 'backend' is not in sys.modules, register it as a virtual package
# pointing to this directory so 'backend.app.*' imports resolve cleanly
# in isolated container builds where parent directory does not exist.
if "backend" not in sys.modules:
    _backend_pkg = types.ModuleType("backend")
    _backend_pkg.__path__ = [str(_backend_dir)]
    sys.modules["backend"] = _backend_pkg

# Also add parent directory to sys.path if accessible (e.g. monorepo root)
_repo_root = str(_backend_dir.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from backend.app.main import app

__all__ = ["app"]
