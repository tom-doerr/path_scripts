#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.text import Text
from rich.table import Table

# Initialize Rich console
console = Console()


def run_command(cmd, cwd=None, capture_output=True, check=True, env=None):
    """Run a shell command and return the result."""
    try:
        # Create a copy of the current environment if needed
        command_env = os.environ.copy()
        if env:
            command_env.update(env)
            
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Running:[/bold blue] {task.description}"),
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task(f"[cyan]{cmd}[/cyan]", total=None)
            result = subprocess.run(
                cmd,
                cwd=cwd,
                shell=True,
                text=True,
                capture_output=capture_output,
                check=check,
                env=command_env
            )
            progress.update(task, completed=True)
        return result
    except subprocess.CalledProcessError as e:
        if capture_output:
            console.print(f"[bold red]Command failed:[/bold red] {cmd}")
            console.print(f"[red]Error:[/red] {e.stderr}")
        return e


def get_repo_name(repo_path):
    """Get the repository name from the git remote URL."""
    result = run_command("git remote get-url origin", cwd=repo_path)
    if result.returncode != 0:
        return "unknown_repo"
    
    remote_url = result.stdout.strip()
    # Extract repo name from URL (works for both HTTPS and SSH URLs)
    repo_name = remote_url.split('/')[-1].replace('.git', '')
    return repo_name


def create_worktree(repo_path, task_name):
    """Create a new git worktree for the task."""
    repo_name = get_repo_name(repo_path)
    worktree_base = os.path.expanduser(f"~/worktrees/{repo_name}")
    
    # Create the base directory if it doesn't exist
    os.makedirs(worktree_base, exist_ok=True)
    
    # Create a sanitized directory name from the task
    safe_task_name = "".join(c if c.isalnum() else "_" for c in task_name)
    safe_task_name = safe_task_name[:50]  # Limit length
    
    # Add timestamp to make it unique
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    worktree_path = os.path.join(worktree_base, f"{safe_task_name}_{timestamp}")
    
    # Get the current branch
    result = run_command("git branch --show-current", cwd=repo_path)
    current_branch = result.stdout.strip()
    
    # Create a new branch for the task
    branch_name = f"task/{safe_task_name}_{timestamp}"
    console.print(f"[bold green]Creating new branch:[/bold green] {branch_name}")
    run_command(f"git branch {branch_name}", cwd=repo_path)
    
    # Create the worktree
    console.print(f"[bold green]Creating worktree at:[/bold green] {worktree_path}")
    run_command(f"git worktree add {worktree_path} {branch_name}", cwd=repo_path)
    
    return worktree_path, branch_name, current_branch


def run_tests(worktree_path):
    """Run pytest and return True if all tests pass."""
    console.print(Panel("[bold]Running Tests[/bold]", style="blue"))
    result = run_command("pytest", cwd=worktree_path, check=False)
    
    if result.returncode == 0:
        console.print(Panel("[bold]All Tests Passed![/bold]", style="green"))
    else:
        console.print(Panel("[bold]Tests Failed[/bold]", style="red"))
    
    return result.returncode == 0


def generate_context(worktree_path):
    """Generate context.txt with test results and linting information."""
    console.print(Panel("[bold]Generating context.txt[/bold]", style="blue"))
    context_file = os.path.join(worktree_path, "context.txt")
    context_tmp = os.path.join(worktree_path, "context.txt.tmp")
    
    # Use a Python context manager to handle file operations
    with open(context_tmp, 'w') as f:
        # Start with date header
        f.write(f"============={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}===================\n\n")
        
        # Check if tests directory exists
        tests_dir = os.path.join(worktree_path, "tests")
        if os.path.exists(tests_dir) and os.path.isdir(tests_dir):
            # Run tests and capture output
            console.print("[dim]Running tests for context...[/dim]")
            result = run_command(
                "python -m pytest --testmon --timeout=10 tests/test*py 2>&1",
                cwd=worktree_path,
                check=False
            )
            # Write up to 500 lines of test output
            test_output = result.stdout.strip().split('\n')[-500:]
            f.write('\n'.join(test_output) + '\n')
        else:
            console.print("[dim]No tests directory found, skipping test execution[/dim]")
            f.write("No tests directory found\n")
        
        # Add separator
        f.write("\n\n\n\n\n=====================================================================\n")
        
        # Find Python files to lint
        result = run_command("git ls-files '*.py'", cwd=worktree_path)
        if result.stdout.strip():
            # Run pylint on all Python files
            console.print("[dim]Running pylint for context...[/dim]")
            lint_result = run_command(
                "pylint $(git ls-files '*.py') 2>&1",
                cwd=worktree_path,
                check=False
            )
            # Write up to 100 lines of lint output
            lint_output = lint_result.stdout.strip().split('\n')[-100:]
            f.write('\n'.join(lint_output) + '\n')
        else:
            console.print("[dim]No Python files found, skipping linting[/dim]")
            f.write("No Python files found for linting\n")
        
        # Add focus on failing tests if tests directory exists
        if os.path.exists(tests_dir) and os.path.isdir(tests_dir):
            f.write("\nFocus on code that causes this test to fail: \n")
            # Find failing tests from the test output
            failing_tests = []
            for line in result.stdout.split('\n'):
                if 'tests/test' in line and ('FAILED' in line or 'ERROR' in line):
                    failing_tests.append(line)
            
            if failing_tests:
                import random
                f.write(random.choice(failing_tests) + '\n')
        
        # Add focus directive
        focus_options = ['Focus on fixing the linting issues', 'Focus on fixing bugs']
        import random
        f.write(f"\n{random.choice(focus_options)}\n")
        
        # Add test files content if they exist
        if os.path.exists(tests_dir) and os.path.isdir(tests_dir):
            test_files = [f for f in os.listdir(tests_dir) if f.endswith('.py')]
            if test_files:
                f.write("\n\n# Test files content:\n")
                for test_file in test_files:
                    test_file_path = os.path.join(tests_dir, test_file)
                    f.write(f"\n# {test_file}\n")
                    with open(test_file_path, 'r') as tf:
                        f.write(tf.read())
    
    # Move temp file to final location
    import shutil
    shutil.move(context_tmp, context_file)
    
    console.print("[dim]Context file generated[/dim]")


def run_aider(worktree_path, task, args, model="r1", inner_loop_count=3):
    """Run aider with the given task."""
    console.print(Panel(f"[bold]Running aider with task:[/bold]\n{task}", style="cyan"))
    
    # Check for instruction file in dotfiles
    instruction_file = os.path.expanduser("~/dotfiles/instruction.md")
    plex_file = "plex.md"
    context_file = "context.txt"
    
    # Setup history file
    history_file = os.path.join(worktree_path, "custom_aider_history.md")
    
    # Run black formatter
    console.print("[dim]Running black formatter...[/dim]")
    run_command("black .", cwd=worktree_path, check=False)
        
    # Prepare read arguments
    read_args = []
    if os.path.exists(instruction_file):
        read_args.append(f"--read {instruction_file}")
        console.print(f"[dim]Using instruction file: {instruction_file}[/dim]")
    
    if os.path.exists(os.path.join(worktree_path, plex_file)):
        read_args.append(f"--read {plex_file}")
        console.print(f"[dim]Using plex file: {plex_file}[/dim]")
    
    worktree_context_file = os.path.join(worktree_path, context_file)
    if os.path.exists(worktree_context_file):
        read_args.append(f"--read {worktree_context_file}")
        console.print(f"[dim]Using context file: {worktree_context_file}[/dim]")
    
    read_args_str = " ".join(read_args)
    
    # Set weak model
    weak_model = "openrouter/google/gemini-2.0-flash-001"
    
    # Using subprocess.run directly to allow interactive session
    console.print(f"[bold yellow]Starting aider session...[/bold yellow]")
    
    # Get repository files without listing them
    result = run_command("git ls-files", cwd=worktree_path)
    all_files = [f for f in result.stdout.strip().split('\n') if f]
    
    # Get full paths for all files
    full_paths = []
    for file_path in all_files:
        full_path = os.path.join(worktree_path, file_path)
        full_paths.append(full_path)
    
    # Check if there are Python files in the repository
    python_files = [f for f in all_files if f.endswith('.py')]
    has_python_files = bool(python_files)
    
    # Log file count
    console.print(f"[dim]Found {len(all_files)} files in repository ({len(python_files)} Python files)[/dim]")
    
    # If no Python files found, create a placeholder file
    if not has_python_files:
        console.print("[dim]No Python files found in repository, creating placeholder...[/dim]")
        placeholder_file = os.path.join(worktree_path, "placeholder.py")
        with open(placeholder_file, "w") as f:
            f.write("# Placeholder file\n# TODO: Add your Python code here\n")
        
        # Add and commit the placeholder file
        run_command("git add placeholder.py", cwd=worktree_path)
        run_command("git commit -m 'Add placeholder Python file'", cwd=worktree_path)
        
        # Update our file lists
        all_files.append("placeholder.py")
        full_paths.append(os.path.join(worktree_path, "placeholder.py"))
    
    # Create the message with the task at the end
    message = f"Improve code quality and fix any issues found in tests or linting. " \
              f"TDD! Add tests for task first before making changes." \
              f"Task: {task}"
    
    # Build the aider command base
    aider_cmd = f"aider --architect --model {model} --weak-model '{weak_model}' {read_args_str}"
    
    # Add remaining arguments
    aider_cmd += (
        f" --yes-always --no-show-model-warnings --no-show-release-notes"
        f" --chat-history-file {history_file} --restore-chat-history"
        f" --edit-format diff --auto-lint --lint-cmd 'pylint'"
        f" --auto-test --test-cmd 'python3.11 -m pytest'"
        f" --message '{message}'"
    )
    
    # Add files based on command line options
    if args.no_python_files:
        file_args = ""
    elif args.all_files:
        file_args = " ".join([f'"{f}"' for f in all_files])
    else:
        file_args = " ".join([f'"{f}"' for f in python_files])
    aider_cmd += f" {file_args}"
    
    # Run aider with proper environment
    console.print(f"[dim]Running aider in {worktree_path}[/dim]")
    subprocess.run(
        aider_cmd,
        cwd=worktree_path,
        shell=True,
        text=True
    )
    
    console.print(f"[bold yellow]Aider session completed[/bold yellow]")
    console.print(f"[dim]{'=' * 50} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {'=' * 50}[/dim]")


def merge_and_push(worktree_path, main_repo_path, branch_name, main_branch, task):
    """Merge changes from main, then push if no conflicts."""
    try:
        # First pull latest changes from main branch
        console.print(f"[bold blue]Pulling latest changes from {main_branch}...[/bold blue]")
        run_command(f"git checkout {main_branch}", cwd=main_repo_path)
        run_command("git pull", cwd=main_repo_path)
        
        # Update the worktree
        console.print("[bold blue]Updating worktree with latest changes...[/bold blue]")
        run_command(f"git pull origin {main_branch}", cwd=worktree_path, check=False)
        
        # Check for merge conflicts
        status = run_command("git status", cwd=worktree_path)
        if "You have unmerged paths" in status.stdout or "fix conflicts" in status.stdout:
            console.print("[bold red]Merge conflicts detected. Running aider to resolve conflicts...[/bold red]")
            
            # Run aider to resolve conflicts
            conflict_task = f"Please resolve the merge conflicts in this repository. Look at the git status output and fix the conflicts. Original task: {task}"
            run_aider(worktree_path, conflict_task, inner_loop_count=1)
            
            # Check if conflicts were resolved
            status = run_command("git status", cwd=worktree_path)
            if "You have unmerged paths" in status.stdout or "fix conflicts" in status.stdout:
                console.print("[bold red]Merge conflicts could not be automatically resolved.[/bold red]")
                return False
        
        # Commit any changes from the merge
        run_command("git commit -am 'Merge from main'", cwd=worktree_path, check=False)
        
        # Run tests to ensure everything still works
        console.print("[bold blue]Running tests after merge...[/bold blue]")
        tests_pass = run_tests(worktree_path)
        if not tests_pass:
            console.print("[bold yellow]Tests failed after merge. Running aider to fix issues...[/bold yellow]")
            fix_task = f"Fix the failing tests after merging with main. Original task: {task}"
            run_aider(worktree_path, fix_task, inner_loop_count=1)
            
            # Check if tests pass now
            tests_pass = run_tests(worktree_path)
            if not tests_pass:
                console.print("[bold red]Tests still failing after attempted fixes.[/bold red]")
                return False
        
        # Push changes to the branch
        console.print(f"[bold blue]Pushing changes to branch {branch_name}...[/bold blue]")
        run_command(f"git push -u origin {branch_name}", cwd=worktree_path)
        
        # Merge back to main if requested
        console.print(f"[bold blue]Merging {branch_name} into {main_branch}...[/bold blue]")
        result = run_command(f"git checkout {main_branch} && git merge {branch_name} && git push", 
                            cwd=main_repo_path, check=False)
        
        if result.returncode != 0:
            console.print("[bold red]Failed to merge to main. Please resolve conflicts manually.[/bold red]")
            return False
        
        console.print(f"[bold green]Successfully merged {branch_name} into {main_branch} and pushed![/bold green]")
        return True
    except Exception as e:
        console.print(f"[bold red]Error during merge and push:[/bold red] {str(e)}")
        return False


def main():
    # Set up signal handlers for graceful exit
    import signal
    
    def signal_handler(sig, frame):
        console.print("\n[bold red]Received interrupt signal. Cleaning up...[/bold red]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    console.print(Panel.fit(
        "[bold cyan]Agent Aider Worktree[/bold cyan]\n"
        "[dim]Create a git worktree and run aider until tests pass, then merge back to main.[/dim]",
        border_style="blue"
    ))
    
    parser = argparse.ArgumentParser(
        description="Create a git worktree and run aider until tests pass, then merge back to main.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Add user authentication feature"
  %(prog)s -p /path/to/repo "Fix bug in login form"
  %(prog)s --model claude-3-opus "Implement new feature"
  %(prog)s --inner-loop 5 "Refactor database code"
        """
    )
    
    parser.add_argument("task", help="The task description to pass to aider")
    parser.add_argument("-p", "--path", default=".", 
                        help="Path to the main git repository (default: current directory)")
    parser.add_argument("--no-push", action="store_true", 
                        help="Don't push changes back to main repository")
    parser.add_argument("--model", default="r1",
                        help="Model to use with aider (default: r1)")
    parser.add_argument("--max-iterations", type=int, default=10,
                        help="Maximum number of iterations to run (default: 10)")
    parser.add_argument("--inner-loop", type=int, default=3,
                        help="Number of inner loop iterations to run (default: 3)")
    parser.add_argument("--all-files", action="store_true",
                        help="Include all files in the repository instead of just Python files")
    parser.add_argument("--no-python-files", action="store_true",
                        help="Disable automatic inclusion of Python files")
    
    args = parser.parse_args()
    
    # Get absolute path to the main repository
    main_repo_path = os.path.abspath(args.path)
    
    # Check if the path is a git repository
    if not os.path.exists(os.path.join(main_repo_path, ".git")):
        console.print(f"[bold red]Error:[/bold red] {main_repo_path} is not a git repository")
        sys.exit(1)
    
    # Create worktree
    worktree_path, branch_name, main_branch = create_worktree(main_repo_path, args.task)
    
    # Initialize iteration counter and start time
    iteration = 1
    start_time = datetime.now()
    
    # Display configuration
    config_table = Table(title="Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_row("Task", args.task)
    config_table.add_row("Repository", main_repo_path)
    config_table.add_row("Worktree", worktree_path)
    config_table.add_row("Branch", branch_name)
    config_table.add_row("Model", args.model)
    config_table.add_row("Max Iterations", str(args.max_iterations))
    config_table.add_row("Push Changes", "No" if args.no_push else "Yes")
    config_table.add_row("Include All Files", "Yes" if args.all_files else "No (Python only)")
    config_table.add_row("Disable Python Files", "Yes" if args.no_python_files else "No")
    console.print(config_table)
    
    # Main loop
    while iteration <= args.max_iterations:
        # Calculate elapsed time
        elapsed_time = datetime.now() - start_time
        elapsed_str = str(elapsed_time).split('.')[0]  # Remove microseconds
        
        console.print(Panel(
            f"[bold]Iteration {iteration}/{args.max_iterations}[/bold]\nTotal time: {elapsed_str}",
            style="blue"
        ))
        
        # Clear previous chat history at the beginning of each outer iteration
        history_file = os.path.join(worktree_path, "custom_aider_history.md")
        if os.path.exists(history_file):
            console.print("[dim]Clearing previous chat history for new iteration...[/dim]")
            open(history_file, 'w').close()  # Empty the file
        
        # Generate context file
        generate_context(worktree_path)
        
        # Run aider
        console.print("[bold blue]Running aider to improve code and fix issues...[/bold blue]")
        run_aider(worktree_path, args.task, args, args.model, 1)
        
        # Check if tests pass after aider run
        console.print("[bold blue]Checking if tests pass...[/bold blue]")
        tests_pass = run_tests(worktree_path)
        
        if tests_pass:
            # Commit any remaining changes
            run_command("git add -A && git commit -m 'Final changes' || true", cwd=worktree_path)
            
            if not args.no_push:
                # Try to merge and push
                merge_success = merge_and_push(worktree_path, main_repo_path, branch_name, main_branch, args.task)
                
                if merge_success:
                    total_time = str(datetime.now() - start_time).split('.')[0]
                    console.print(Panel(
                        f"[bold]Task completed successfully in {iteration} iterations![/bold]\n"
                        f"Total time: {total_time}",
                        style="green"
                    ))
                    break
                else:
                    console.print("[yellow]Merge conflicts detected. Running aider again to resolve conflicts...[/yellow]")
                    iteration += 1
                    if iteration > args.max_iterations:
                        console.print(Panel(
                            f"[bold]Reached maximum number of iterations ({args.max_iterations})[/bold]\n"
                            f"Total time spent: {str(datetime.now() - start_time).split('.')[0]}\n"
                            "Exiting without completing the task.",
                            style="red"
                        ))
                        break
                    continue
            else:
                total_time = str(datetime.now() - start_time).split('.')[0]
                console.print(Panel(
                    f"[bold]Task completed successfully in {iteration} iterations![/bold]\n"
                    f"Total time: {total_time}",
                    style="green"
                ))
                break
        else:
            console.print("[yellow]Tests failed. Running aider again...[/yellow]")
            iteration += 1
            
            if iteration > args.max_iterations:
                console.print(Panel(
                    f"[bold]Reached maximum number of iterations ({args.max_iterations})[/bold]\n"
                    f"Total time spent: {str(datetime.now() - start_time).split('.')[0]}\n"
                    "Exiting without completing the task.",
                    style="red"
                ))
                break


if __name__ == "__main__":
    main()
