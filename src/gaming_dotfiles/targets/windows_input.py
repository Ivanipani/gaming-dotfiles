"""Windows mouse and keyboard settings (pointer speed/acceleration, key repeat)."""

import json
import re
from pathlib import Path

from gaming_dotfiles import files, host

# Seeds the first capture; afterwards the repo file defines which values are managed.
DEFAULT_VALUES = {
    r"HKCU\Control Panel\Mouse": [
        "MouseSensitivity",
        "MouseSpeed",
        "MouseThreshold1",
        "MouseThreshold2",
        "SmoothMouseXCurve",
        "SmoothMouseYCurve",
        "SwapMouseButtons",
        "DoubleClickSpeed",
    ],
    r"HKCU\Control Panel\Keyboard": ["KeyboardDelay", "KeyboardSpeed"],
}
VALUE_LINE = re.compile(r"^ {4}(.+?) {4}(REG_\w+) {4}(.*)$")


def _query(key: str) -> dict[str, dict[str, str]]:
    values = {}
    for line in host.run("reg.exe", "query", key).splitlines():
        if m := VALUE_LINE.match(line):
            values[m[1]] = {"type": m[2], "data": m[3]}
    return values


class WindowsInput:
    name = "windows"

    def __init__(self, cfg: dict, repo: Path):
        self.repo_file = repo / "windows" / "input.json"

    def _desired(self) -> dict:
        return json.loads(self.repo_file.read_text())

    def _live(self, managed: dict[str, list[str]]) -> dict:
        live = {}
        for key, names in managed.items():
            values = _query(key)
            live[key] = {n: values[n] for n in names if n in values}
        return live

    def capture(self) -> None:
        managed = (
            {k: list(v) for k, v in self._desired().items()} if self.repo_file.exists() else DEFAULT_VALUES
        )
        self.repo_file.parent.mkdir(parents=True, exist_ok=True)
        self.repo_file.write_text(files.dump_json(self._live(managed)))
        print(f"windows: captured {self.repo_file.name}")

    def diff(self) -> list[str]:
        if not self.repo_file.exists():
            return [f"missing in repo: {self.repo_file}"]
        desired = self._desired()
        return files.diff_json(self.repo_file.name, desired, self._live(desired))

    def apply(self) -> None:
        for key, values in self._desired().items():
            for name, v in values.items():
                host.run("reg.exe", "add", key, "/v", name, "/t", v["type"], "/d", v["data"], "/f")
        print("windows: applied (sign out and back in for it to take effect)")
