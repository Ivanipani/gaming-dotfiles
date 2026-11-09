# Targets: league, logitech, razer, windows (omit for all enabled)

# Show available recipes
[private]
default:
    @just --list --unsorted

# Pull live settings from Windows into config/ (review with `jj diff`, then commit)
capture *targets:
    uv run gaming-dotfiles capture {{targets}}

# Show drift between config/ and the live machine (exit 1 on drift)
diff *targets:
    uv run gaming-dotfiles diff {{targets}}

# Push config/ to the live machine (quit G HUB first for logitech)
apply *targets:
    uv run gaming-dotfiles apply {{targets}}

# Fetch the latest config from the remote and apply it
sync *targets:
    jj git fetch
    jj new 'trunk()'
    just apply {{targets}}
