"""Tests for core agent functionality."""

from src.agent.core import Agent  # pylint: disable=no-name-in-module


def test_agent_initialization():
    """Test agent initializes with correct repository info."""
    test_repo_path = "/test/path"
    agent = Agent()
    
    # Test initial state before initialization
    assert not agent.repository_info  # Should be empty
    
    agent.initialize(test_repo_path)
    
    # Test state after initialization
    assert "path" in agent.repository_info
    assert agent.repository_info["path"] == test_repo_path

def test_agent_initial_state():
    """Test agent starts with empty repository info."""
    agent = Agent()
    assert agent.repository_info == {}, "Repository info should be empty before initialization"
