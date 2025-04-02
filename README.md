# Path Scripts

A collection of powerful CLI tools for automating development workflows and task management. These scripts are designed to be added to your system PATH for easy command-line access.

Repository: https://github.com/tom-doerr/path_scripts

## Tools Overview

### 1. Agent Aider Worktree

Automates code improvements using AI agents in isolated git worktrees.

#### Key Features
- Creates isolated git worktrees for safe experimentation
- Runs AI-powered code analysis and improvements
- Automatically merges changes back to main branch
- Handles merge conflicts intelligently
- Test-driven development workflow
- Exponential retry strategy for complex tasks

#### Installation
```bash
# Clone and install
git clone https://github.com/tom-doerr/path_scripts.git
cd path_scripts
pip install -r requirements.txt

# Add to PATH (optional)
ln -s $PWD/agent-aider-worktree ~/.local/bin/
```

#### Usage
```bash
# Basic usage
agent-aider-worktree "Add user authentication"

# With custom iterations and model
agent-aider-worktree --max-iterations 20 --model claude-3-opus "Refactor database code"

# From a subdirectory
agent-aider-worktree --exponential-retries "Fix login form validation"
```

#### Command Line Options
| Option | Description | Default |
|--------|-------------|---------|
| `--path` | Repository path | Current directory |
| `--model` | AI model to use | deepseek-reasoner |
| `--weak-model` | Secondary model | deepseek |
| `--max-iterations` | Maximum iterations | 10 |
| `--inner-loop` | Inner loop iterations | 10 |
| `--exponential-retries` | Use exponential retry strategy | False |
| `--no-push` | Skip pushing changes | False |
| `--read` | Additional files to analyze | [] |

### 2. Aider Multi-Agent System

Runs multiple AI agents in parallel for distributed code analysis.

#### Key Features
- Parallel agent execution in tmux sessions
- Configurable models and iterations
- Session persistence and recovery
- Centralized management interface

#### Usage
```bash
# Start 3 parallel agents
aider_multi_agent -n 3

# Use specific model
aider_multi_agent -m claude-3-opus -n 2

# Kill all sessions
aider_multi_agent -k
```

#### Options
| Option | Description | Default |
|--------|-------------|---------|
| `-n SESSIONS` | Number of agents | 1 |
| `-m MODEL` | AI model | r1 |
| `-w WEAK_MODEL` | Secondary model | gemini-2.0-flash-001 |
| `-i ITERATIONS` | Max iterations | 1000 |
| `-k` | Kill all sessions | - |

### 3. Task Management (c)

Streamlined interface for Taskwarrior with smart filtering.

#### Installation
```bash
# Install to PATH
cp c ~/.local/bin/
chmod +x ~/.local/bin/c

# Configure task script path
export TASK_SCRIPT_PATH="/path/to/show_tw_tasks.py"
```

#### Usage
```bash
# Show pending tasks
c

# Filter by tag and report
c "+work" "active"

# Custom filters
c -n "+project:home" "next"
```

## Dependencies

- Python 3.8+
- Git 2.25+
- tmux
- Taskwarrior (for task management)
- Required Python packages in requirements.txt

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details
