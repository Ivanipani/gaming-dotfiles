"""Gaming settings as code: capture live settings, diff for drift, apply the repo."""

import argparse
import sys
import tomllib
from pathlib import Path

from gaming_dotfiles.targets import TARGETS, Target

CONFIG_NAME = "gaming-dotfiles.toml"


def find_repo() -> Path:
    for start in (Path.cwd(), Path(__file__).resolve()):
        for d in (start, *start.parents):
            if (d / CONFIG_NAME).exists():
                return d
    raise SystemExit(f"{CONFIG_NAME} not found")


def load_targets(names: list[str]) -> list[Target]:
    repo = find_repo()
    cfg = tomllib.loads((repo / CONFIG_NAME).read_text())
    enabled = [n for n in TARGETS if cfg.get(n, {}).get("enabled", True)]
    if unknown := set(names) - set(TARGETS):
        raise SystemExit(f"unknown targets: {', '.join(sorted(unknown))}")
    return [TARGETS[n](cfg.get(n, {}), repo / "config") for n in names or enabled]


def main() -> None:
    parser = argparse.ArgumentParser(prog="gaming-dotfiles", description=__doc__)
    parser.add_argument("command", choices=("capture", "diff", "apply"))
    parser.add_argument("targets", nargs="*", help=f"subset of: {', '.join(TARGETS)}")
    args = parser.parse_args()

    drifted = False
    for target in load_targets(args.targets):
        if args.command == "diff":
            drift = target.diff()
            drifted |= bool(drift)
            print(f"== {target.name}: {'drift' if drift else 'in sync'}")
            if drift:
                print(*drift, sep="\n")
        else:
            getattr(target, args.command)()
    sys.exit(1 if drifted else 0)
