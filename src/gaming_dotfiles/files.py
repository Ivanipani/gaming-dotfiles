"""Shared file and JSON drift helpers."""

import difflib
import json
from pathlib import Path

from gaming_dotfiles import host


def _lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def diff_file(repo: Path, live: Path) -> list[str]:
    if not repo.exists():
        return [f"missing in repo: {repo}"]
    if not live.exists():
        return [f"missing on host: {live}"]
    if repo.read_bytes() == live.read_bytes():
        return []
    return list(
        difflib.unified_diff(_lines(repo), _lines(live), f"repo/{repo.name}", f"live/{live.name}", lineterm="")
    )


def diff_json(name: str, desired: object, actual: object) -> list[str]:
    a, b = dump_json(desired).splitlines(), dump_json(actual).splitlines()
    return list(difflib.unified_diff(a, b, f"repo/{name}", f"live/{name}", lineterm=""))


def dump_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def copy(src: Path, dst: Path, readonly: bool = False) -> None:
    """Copy bytes, temporarily unlocking a read-only destination."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        host.set_readonly(dst, False)
    dst.write_bytes(src.read_bytes())
    if readonly:
        host.set_readonly(dst, True)
