#!/usr/bin/env python3
"""Repository analysis functionality."""

import os
import subprocess
from typing import Dict, Any, List

def analyze_repository(repo_path: str = ".") -> Dict[str, Any]:
    """
    Analyze the repository structure and return information.
    
    Args:
        repo_path: Path to the repository to analyze
        
    Returns:
        Dictionary containing repository information
    """
    repo_info = {
        "files": [],
        "directories": [],
        "git_info": {}
    }
    
    # Get list of files (excluding .git directory)
    try:
        result = subprocess.run(
            ["git", "ls-files"], 
            cwd=repo_path,
            capture_output=True, 
            text=True, 
            check=True
        )
        repo_info["files"] = result.stdout.strip().split("\n")
    except subprocess.CalledProcessError:
        # Fallback if git command fails
        for root, dirs, files in os.walk(repo_path):
            if ".git" in root:
                continue
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, repo_path)
                repo_info["files"].append(rel_path)
            for dir in dirs:
                if dir != ".git":
                    full_path = os.path.join(root, dir)
                    rel_path = os.path.relpath(full_path, repo_path)
                    repo_info["directories"].append(rel_path)
    
    # Get git info if available
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"], 
            cwd=repo_path,
            capture_output=True, 
            text=True, 
            check=True
        )
        repo_info["git_info"]["current_branch"] = result.stdout.strip()
    except subprocess.CalledProcessError:
        repo_info["git_info"]["current_branch"] = "unknown"
        
    return repo_info


if __name__ == "__main__":
    # Simple test when run directly
    import json
    repo_info = analyze_repository()
    print(json.dumps(repo_info, indent=2))
