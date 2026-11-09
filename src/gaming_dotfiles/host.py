"""Helpers for reaching the Windows host from WSL (or running natively on Windows)."""

import functools
import os
import stat
import subprocess
import sys
from pathlib import Path

IS_WSL = sys.platform == "linux" and "microsoft" in os.uname().release.lower()


def run(*args: str) -> str:
    # cwd on a Windows drive avoids cmd.exe's UNC-path warning.
    cwd = "/mnt/c" if IS_WSL else None
    result = subprocess.run(args, capture_output=True, text=True, check=True, cwd=cwd)
    return result.stdout.replace("\r", "")


def to_local(win_path: str) -> Path:
    return Path(run("wslpath", "-u", win_path).strip()) if IS_WSL else Path(win_path)


def to_windows(path: Path) -> str:
    return run("wslpath", "-w", str(path)).strip() if IS_WSL else str(path)


@functools.cache
def win_env(name: str) -> Path:
    if not IS_WSL:
        return Path(os.environ[name])
    return to_local(run("cmd.exe", "/c", f"echo %{name}%").strip())


def is_running(image: str) -> bool:
    out = run("tasklist.exe", "/FI", f"IMAGENAME eq {image}", "/NH", "/FO", "CSV")
    return image.lower() in out.lower()


def set_readonly(path: Path, readonly: bool) -> None:
    # On DrvFs, clearing the write bits sets the Windows read-only attribute.
    mode = path.stat().st_mode
    write = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
    path.chmod(mode & ~write if readonly else mode | stat.S_IWUSR)


def is_readonly(path: Path) -> bool:
    return not path.stat().st_mode & stat.S_IWUSR
