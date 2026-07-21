from __future__ import annotations

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]


def copy_project(destination: Path) -> Path:
    project = destination / "project"
    shutil.copytree(
        ROOT,
        project,
        ignore=shutil.ignore_patterns(".git", ".DS_Store", "__pycache__", "*.pyc", "dist"),
    )
    return project
