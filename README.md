<p align="center">
  <img src="assets/banner.svg" alt="dirdiff" width="100%">
</p>

**dirdiff** compares two folders by *content* and tells you what is only in A, only in B, or changed. One Python file, zero dependencies.

## Why

Checking a backup, a deploy folder or a build output against the original usually means eyeballing file lists. `dirdiff` hashes files (SHA-256) so renamed timestamps do not fool it, and it exits with a CI-friendly status code.

## Usage

```bash
python3 dirdiff.py folder_a folder_b
```

```text
- old_notes.txt
+ new_feature.py
~ config.json

1 only in A, 1 only in B, 1 changed, 42 identical
```

`-` only in A, `+` only in B, `~` content differs.

## Options

| Option | What it does |
| --- | --- |
| `-i GLOB`, `--ignore GLOB` | Ignore files/folders matching a glob (repeatable) |
| `--no-default-ignore` | Also look inside `.git`, `__pycache__`, `node_modules` |
| `-q`, `--quick` | Compare size + mtime instead of hashing (faster) |
| `--json` | Machine-readable output |

Exit code: `0` identical, `1` differences found, `2` bad input.

## CI example

```bash
python3 dirdiff.py build/ expected/ --json > diff.json || echo "Output changed"
```

## Requirements

Python 3.8+. Nothing to install.
