# Contributing to Hermes Skins

## Creating a Skin

1. Copy `template.yaml` to `skins/<name>.yaml`
2. Set `name:` to match the filename (without `.yaml`)
3. Customize colors, spinner, branding, and optionally `banner_logo` / `banner_hero`
4. Add a brief description comment at the top of the file

### Naming Conventions

- Lowercase kebab-case: `my-skin.yaml`, not `MySkin.yaml` or `my_skin.yaml`
- The `name:` field inside the YAML must match the filename exactly

### Colors

All color values must be hex strings in `#RRGGBB` format (e.g., `"#FFD700"`). No shorthand, no named colors, no RGBA.

## Testing Locally

Requires [Hermes](https://github.com/NousResearch/hermes-agent) installed.

```bash
cp skins/<name>.yaml ~/.hermes/skins/<name>.yaml
```

Then inside Hermes:
```
/skin <name>
```

Missing values inherit from the `default` skin, so partial skins work fine.

## Generating Screenshots

The screenshot generator requires:
- Python dependencies: `pip install -r requirements.txt`
- Chromium/Chrome installed (used by `html2image`)
- The `hermes-agent` repo cloned locally

By default the script looks for hermes-agent at `~/projects/hermes-agent`. Override with an environment variable:

```bash
HERMES_AGENT_DIR=/path/to/hermes-agent python3 generate_screenshots.py
```

Screenshots are saved to `screenshots/<name>.png`.

## Submitting a PR

Checklist before opening a pull request:

- [ ] `skins/<name>.yaml` added
- [ ] `name:` key matches filename
- [ ] Screenshot generated and committed to `screenshots/<name>.png`
- [ ] Entry added to the **Custom** section of `README.md`
- [ ] Brief description comment at the top of the YAML file
- [ ] `python3 validate_skins.py` passes with no errors

## Schema Reference

See [SCHEMA.md](SCHEMA.md) for the full list of configurable keys, their types, and defaults.
