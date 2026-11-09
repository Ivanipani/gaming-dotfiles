"""Razer Synapse 4 (Tartarus V2).

Synapse 4 keeps profiles in Chromium storage and Razer's cloud, with no file to
reconcile, so the versioned artifact is a Synapse profile export (*.synapse4)
imported through the Synapse UI.
"""

from pathlib import Path

from gaming_dotfiles import host


class Razer:
    name = "razer"

    def __init__(self, cfg: dict, repo: Path):
        self.dir = repo / "razer"
        self.exports = cfg.get("exports", ["tartarus_v2.synapse4"])

    def _missing(self) -> list[Path]:
        return [self.dir / e for e in self.exports if not (self.dir / e).exists()]

    def capture(self) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        print(f"razer: in Synapse, Tartarus V2 > Profiles > Export, and save into {host.to_windows(self.dir)}")

    def diff(self) -> list[str]:
        return [f"missing in repo: {p} (export it from Synapse)" for p in self._missing()]

    def apply(self) -> None:
        present = [self.dir / e for e in self.exports if (self.dir / e).exists()]
        for p in present:
            print(f"razer: in Synapse, Tartarus V2 > Profiles > Import, and pick {host.to_windows(p)}")
