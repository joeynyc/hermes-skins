# Hermes Skins

Custom skins (visual themes) for the [Hermes](https://github.com/NousResearch/hermes-agent) CLI agent.

Skins control the **visual presentation** of Hermes: banner colors, spinner faces/verbs, response-box labels, branding text, tool activity prefix, and ASCII art banners. They don't affect personality or behavior — just how things look.

## Quick Start

1. Browse the `skins/` directory and pick one you like
2. Copy the `.yaml` file to `~/.hermes/skins/`
3. Activate it:

```bash
# Session-only
/skin pirate

# Permanent (add to ~/.hermes/config.yaml)
display:
  skin: pirate
```

That's it. Missing values inherit from the default skin, so you only need to define what you want to change.

## Available Skins

### Custom

| Skin | Description | Preview |
|------|-------------|---------|
| [pirate](skins/pirate.yaml) | Black & white pirate flag theme with skull-and-crossbones braille art | Monochrome, nautical |
| [vault-tec](skins/vault-tec.yaml) | Fallout Vault-Tec terminal — green phosphor CRT on black | Green-on-black, retro CRT |

### Built-in (ship with Hermes)

These are included for reference. They're already available in every Hermes install.

| Skin | Description |
|------|-------------|
| default | Classic gold and kawaii |
| ares | Crimson and bronze war-god |
| mono | Clean grayscale monochrome |
| slate | Cool blue developer-focused |
| poseidon | Deep blue and seafoam ocean-god |
| sisyphus | Austere grayscale with persistence |
| charizard | Burnt orange and ember volcanic |

## Creating Your Own

Drop a YAML file in `~/.hermes/skins/<name>.yaml`. The `name:` field inside must match the filename.

### Minimal Example

```yaml
name: cyberpunk
description: Neon terminal theme

colors:
  banner_border: "#FF00FF"
  banner_title: "#00FFFF"
  banner_accent: "#FF1493"

spinner:
  thinking_verbs: ["jacking in", "decrypting", "uploading"]

branding:
  agent_name: "Cyber Agent"
  response_label: " ⚡ Cyber "
```

Everything you don't specify inherits from the `default` skin.

### Full Schema

See [SCHEMA.md](SCHEMA.md) for the complete list of configurable keys.

## Contributing

Made a skin you're proud of? PRs welcome.

1. Add your `.yaml` to `skins/`
2. Include a brief description at the top
3. Make sure it has a `name:` key matching the filename
4. Update the table in this README

## How Skins Work

Hermes loads skins from two locations (user skins take priority):
1. `~/.hermes/skins/<name>.yaml` (user custom)
2. Built-in skins hardcoded in `skin_engine.py`

The engine merges your skin on top of `default`, so partial skins work fine. Unknown skin names silently fall back to `default`.

## License

MIT
