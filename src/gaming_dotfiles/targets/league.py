"""League of Legends client/game settings.

Locking the live files read-only stops the client from replacing them with each
account's cloud-synced copy at login, so every account gets the repo's settings.
Profiles are also mirrored into league-config-manager so its GUI and per-champion
auto-swap operate on the versioned profiles.
"""

import json
from pathlib import Path

from gaming_dotfiles import files, host

FILES = ("game.cfg", "input.ini", "PersistedSettings.json")


class League:
    name = "league"

    def __init__(self, cfg: dict, repo: Path):
        self.install_dir = cfg["install_dir"]
        self.live = host.to_local(self.install_dir) / "Config"
        self.profiles = repo / "league"
        self.active = cfg.get("active_profile", "default")
        self.lock = cfg.get("lock", True)
        self.sync_to_app = cfg.get("sync_to_app", True)

    def _pairs(self) -> list[tuple[Path, Path]]:
        return [(self.profiles / self.active / f, self.live / f) for f in FILES]

    def capture(self) -> None:
        for repo, live in self._pairs():
            files.copy(live, repo)
        print(f"league: captured into profile '{self.active}'")

    def diff(self) -> list[str]:
        drift = [line for repo, live in self._pairs() for line in files.diff_file(repo, live)]
        if self.lock and any(live.exists() and not host.is_readonly(live) for _, live in self._pairs()):
            drift.append("live settings are not locked read-only")
        return drift

    def apply(self) -> None:
        for repo, live in self._pairs():
            files.copy(repo, live, readonly=self.lock)
        print(f"league: applied profile '{self.active}'" + (" (locked)" if self.lock else ""))
        if self.sync_to_app:
            self._sync_app()

    def _sync_app(self) -> None:
        # league-config-manager: %APPDATA%\league_config_manager\data\{config.json,<profile>/}
        data = host.win_env("APPDATA") / "league_config_manager" / "data"
        for profile in sorted(p for p in self.profiles.iterdir() if p.is_dir()):
            for f in FILES:
                if (profile / f).exists():
                    files.copy(profile / f, data / profile.name / f)
        (data / "config.json").write_text(json.dumps({"path": self.install_dir}))
        print(f"league: synced profiles to league-config-manager ({data})")
