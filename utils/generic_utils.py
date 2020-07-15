from pathlib import Path


def project_root_path() -> Path:
    return Path(__file__).parent.parent
