"""Logitech G HUB (G502 Wireless): profiles, button assignments, DPI cards.

G HUB keeps its state as one JSON blob in a WAL-mode SQLite DB. The DB is copied
locally to read/write it, since SQLite's shared memory doesn't work over DrvFs.
"""

import datetime
import json
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path

from gaming_dotfiles import files, host

# Built-in preset cards are flagged readOnly; G HUB owns those.
MANAGED_KEYS = ("applications", "cards", "profiles")
PROCESSES = ("lghub.exe", "lghub_agent.exe")
DB_FILES = ("settings.db", "settings.db-wal", "settings.db-shm")


class Logitech:
    name = "logitech"

    def __init__(self, cfg: dict, repo: Path):
        self.db_dir = host.win_env("LOCALAPPDATA") / "LGHUB"
        self.repo_file = repo / "logitech" / "ghub.json"
        self.backups = Path.home() / ".local/state/gaming-dotfiles/backups/ghub"

    @contextmanager
    def _db(self):
        with tempfile.TemporaryDirectory() as tmp:
            for f in DB_FILES:
                if (self.db_dir / f).exists():
                    shutil.copyfile(self.db_dir / f, Path(tmp) / f)
            con = sqlite3.connect(Path(tmp) / "settings.db")
            try:
                yield con, Path(tmp) / "settings.db"
            finally:
                con.close()

    @staticmethod
    def _read(con: sqlite3.Connection) -> tuple[int, dict]:
        row_id, blob = con.execute("SELECT _id, file FROM data ORDER BY _id DESC LIMIT 1").fetchone()
        return row_id, json.loads(blob)

    @staticmethod
    def _managed(data: dict) -> dict:
        managed = {k: data[k] for k in MANAGED_KEYS}
        managed["cards"] = {"cards": [c for c in data["cards"]["cards"] if not c.get("readOnly")]}
        return managed

    def _live(self) -> dict:
        with self._db() as (con, _):
            return self._managed(self._read(con)[1])

    def capture(self) -> None:
        self.repo_file.parent.mkdir(parents=True, exist_ok=True)
        self.repo_file.write_text(files.dump_json(self._live()))
        print(f"logitech: captured {self.repo_file.name}")

    def diff(self) -> list[str]:
        if not self.repo_file.exists():
            return [f"missing in repo: {self.repo_file}"]
        return files.diff_json(self.repo_file.name, json.loads(self.repo_file.read_text()), self._live())

    def apply(self) -> None:
        if running := [p for p in PROCESSES if host.is_running(p)]:
            raise SystemExit(f"logitech: quit G HUB first (running: {', '.join(running)})")
        desired = json.loads(self.repo_file.read_text())
        self._backup()
        with self._db() as (con, db):
            row_id, data = self._read(con)
            presets = [c for c in data["cards"]["cards"] if c.get("readOnly")]
            data.update(desired)
            data["cards"] = {**desired["cards"], "cards": presets + desired["cards"]["cards"]}
            con.execute("UPDATE data SET file = ? WHERE _id = ?", (json.dumps(data).encode(), row_id))
            con.commit()
            # Fold the WAL into the main file so a single file can be written back.
            con.execute("PRAGMA journal_mode=DELETE")
            con.close()
            shutil.copyfile(db, self.db_dir / "settings.db")
        for f in DB_FILES[1:]:
            (self.db_dir / f).unlink(missing_ok=True)
        print("logitech: applied (start G HUB to load it)")

    def _backup(self) -> None:
        dest = self.backups / datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        dest.mkdir(parents=True)
        for f in DB_FILES:
            if (self.db_dir / f).exists():
                shutil.copyfile(self.db_dir / f, dest / f)
        print(f"logitech: backed up DB to {dest}")
