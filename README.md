# Personal PATH Scripts Repository

Collection of utility scripts designed to be added to system PATH for easy command-line access

## Primary Script: Taskwarrior Task Viewer (c)

Simple bash wrapper for viewing Taskwarrior tasks with common filters

## Installation

This repository contains personal scripts intended to be available system-wide via PATH:

```bash
# Make executable and install to PATH
chmod +x c
sudo mv c /usr/local/bin/  # Or ~/.local/bin/ for user-specific install

# Edit the script to point to your show_tw_tasks.py location
```

## Usage

Basic usage with default filters (+PENDING -bu):
```bash
c
```

With additional filters and report name:
```bash
c "+work" "active" my_report
```

Disable default filters:
```bash
c -n "+customfilter" 
c --no_default_filters "+otherfilter"
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `-n`, `--no_default_filters` | Disable default task filters |

## Dependencies

Requires tasklib and a local copy of `show_tw_tasks.py` from the user's scripts repository

**Note:** The script contains an absolute path to `show_tw_tasks.py` that users will need to modify for their system
