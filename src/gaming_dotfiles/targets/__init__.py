from pathlib import Path
from typing import Protocol

from gaming_dotfiles.targets.league import League
from gaming_dotfiles.targets.logitech import Logitech
from gaming_dotfiles.targets.razer import Razer
from gaming_dotfiles.targets.windows_input import WindowsInput


class Target(Protocol):
    name: str

    def __init__(self, cfg: dict, repo: Path) -> None: ...
    def capture(self) -> None: ...
    def diff(self) -> list[str]: ...
    def apply(self) -> None: ...


TARGETS: dict[str, type[Target]] = {t.name: t for t in (League, Logitech, Razer, WindowsInput)}
