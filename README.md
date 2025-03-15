# Personal PATH Scripts Repository

Collection of utility scripts designed to be added to system PATH for easy command-line access

## Scripts

### 1. Taskwarrior Task Viewer (c)

Simple bash wrapper for viewing Taskwarrior tasks with common filters

#### Installation
```bash
# Make executable and install to PATH
chmod +x c
sudo mv c /usr/local/bin/  # Or ~/.local/bin/ for user-specific install

# Edit the script to point to your show_tw_tasks.py location
```

#### Usage
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

#### Command Line Options
| Option | Description |
|--------|-------------|
| `-n`, `--no_default_filters` | Disable default task filters |

#### Dependencies
Requires tasklib and a local copy of `show_tw_tasks.py` from the user's scripts repository

**Note:** The script contains an absolute path to `show_tw_tasks.py` that users will need to modify for their system

---

### 2. Aider Multi-Agent System

A script to run multiple aider agents in parallel using tmux for code analysis and improvement.

#### Installation
```bash
chmod +x aider_multi_agent
sudo mv aider_multi_agent /usr/local/bin/  # Optional: for global access
```

#### Usage
Start multiple sessions:
```bash
aider_multi_agent -n 3  # Starts 3 horizontal splits
```

Stop all sessions:
```bash
aider_multi_agent -k
```

Check running sessions:
```bash
tmux list-sessions | grep aider_multi_agent
```

#### Options
```
-h, --help      Show help message
-i ITERATIONS   Number of iterations (default: 1000)
-m MODEL        Model to use (default: r1)
-w WEAK_MODEL   Weak model to use (default: gemini-2.0-flash-001)
-n SESSIONS     Number of tmux sessions (default: 1)
-k              Kill all running sessions
```

#### Features
- Parallel execution in tmux sessions
- Horizontal splits for multiple agents 
- Centralized session management
- Configurable models and iterations
- Automatic history management
- Parallel task execution
- Session persistence and recovery
