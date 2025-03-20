"""Tests for task execution functionality."""

from src.agent.task import execute_task
from src.agent.core import Agent

def test_execute_task_with_no_plan():
    """Test executing a task when no plan exists."""
    agent = Agent()
    
    # Execute task with no plan
    result = execute_task(agent, "task1")
    
    # Verify error response
    assert "error" in result
    assert "No plan exists" in result
