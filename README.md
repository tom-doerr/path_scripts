# Taskwarrior Task Viewer (c)

Simple bash wrapper for viewing Taskwarrior tasks with common filters

## Installation

```bash
chmod +x c
# Optional: Move to somewhere in your PATH
# sudo mv c /usr/local/bin/
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

Requires `show_tw_tasks.py` and its dependencies (tasklib, click)
