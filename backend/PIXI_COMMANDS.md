# Pixi Quick Reference for MAD Backend

## Initial Setup

```bash
# Install pixi (only once)
curl -fsSL https://pixi.sh/install.sh | bash

# Or on macOS
brew install pixi

# Install project dependencies
pixi install
```

## Running the Server

```bash
# Development mode (with auto-reload)
pixi run dev

# Production mode
pixi run start
```

## Testing & Health Checks

```bash
# Run API tests
pixi run test

# Check API health
pixi run health

# List all posters
pixi run posters
```

## Managing Dependencies

```bash
# Add a new package
pixi add <package-name>

# Add a PyPI package
pixi add --pypi <package-name>

# Update all dependencies
pixi update

# Show installed packages
pixi list
```

## Environment Management

```bash
# Show info about the environment
pixi info

# Clean the environment
pixi clean

# Reinstall everything
pixi install --force
```

## Running Custom Commands

```bash
# Run any Python script in the environment
pixi run python script.py

# Run any command in the environment
pixi run <command>

# Shell into the environment
pixi shell
```

## Why Pixi?

- **Reproducible**: Lock file ensures everyone has the same dependencies
- **Fast**: Uses conda-forge for binary packages (no compilation)
- **Cross-platform**: Works on Linux, macOS, Windows
- **Self-contained**: No need for virtualenv or conda activate
- **Task runner**: Built-in task management (see pixi.toml)

## Useful Files

- `pixi.toml` - Project configuration and dependencies
- `pixi.lock` - Lock file (auto-generated, commit to git)
- `.pixi/` - Environment directory (ignored by git)

## Switching from pip

All your `requirements.txt` dependencies are now in `pixi.toml`:

- Just run `pixi install` instead of `pip install -r requirements.txt`
- Use `pixi run` instead of `python` for running scripts
- Everything else works the same!

## Advanced: Multiple Environments

```bash
# Run with dev tools (black, ruff, mypy)
pixi run --environment dev <command>

# Default environment has just the runtime dependencies
pixi run <command>
```

## Troubleshooting

### Pixi not found after install

Restart your shell or run:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### Can't install a package

Try specifying the channel:
```bash
pixi add --channel conda-forge <package>
```

Or use PyPI for Python-only packages:
```bash
pixi add --pypi <package>
```

### Environment is broken

Clean and reinstall:
```bash
pixi clean
pixi install
```

## More Info

- Pixi documentation: https://pixi.sh
- GitHub: https://github.com/prefix-dev/pixi
