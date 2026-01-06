"""
Utility functions for Risk Analytics Project
Handles configuration, hashing, Git commit tracking, and directory setup.
"""

import os
import hashlib
import subprocess
import yaml


def load_config(path: str) -> dict:
    """Load YAML configuration file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def sha256(path: str) -> str:
    """Compute SHA256 hash of a file for audit snapshots."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def try_git_commit_hash():
    """Get current Git commit hash (if repo available)."""
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return None


def ensure_dirs(*dirs):
    """Ensure output directories exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)
