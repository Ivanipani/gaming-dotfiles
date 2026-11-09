# gaming-dotfiles

Gaming settings as code. `config/` is the desired state; the CLI reconciles it with the Windows host (run from WSL).

| Target     | What                                   | Live location                                         | Apply                          |
|------------|----------------------------------------|-------------------------------------------------------|--------------------------------|
| `league`   | game.cfg, input.ini, PersistedSettings | `<install_dir>\Config`                                | copy + lock read-only          |
| `logitech` | G502 profiles, buttons, DPI            | `%LOCALAPPDATA%\LGHUB\settings.db`                    | DB write (G HUB must be closed)|
| `razer`    | Tartarus V2 Synapse export             | Synapse 4 (cloud, no file)                            | manual import via Synapse      |
| `windows`  | pointer speed/accel, key repeat        | `HKCU\Control Panel\{Mouse,Keyboard}`                 | `reg add` (sign out/in)        |

## Workflow

```sh
just capture          # live -> config/
jj diff               # review
jj commit -m "feat(league): lower camera sensitivity"
just diff             # check for drift
just apply            # config/ -> live
just sync             # fetch latest, then apply
```

## League: same settings on every account

The client replaces local settings with each account's cloud copy (`PersistedSettings.json`) at login.
`lock = true` marks the files read-only so that can't happen and every account loads the repo's settings.
Unlock to change settings in-game: `lock = false`, `just apply league`, change settings, `just capture league`, and set `lock = true` again.

Each folder in `config/league/` is a profile; `active_profile` picks the one applied to the game.
With `sync_to_app = true`, all profiles are mirrored into [league-config-manager](https://github.com/brkicdusan/league-config-manager/releases) (Windows `.exe`; only needed for its GUI/auto-swap), so its GUI and per-champion auto-swap use these profiles.
Profile champion bindings (`settings.json`) stay owned by that app.

## Razer Tartarus V2

Synapse 4 keeps no local config file. Export the profile from Synapse into `config/razer/tartarus_v2.synapse4`
(`just capture razer` prints the path), and import it from there on a new machine.

G HUB DB backups are saved to `~/.local/state/gaming-dotfiles/backups/ghub/` before each apply.
