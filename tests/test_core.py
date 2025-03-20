"""Tests for core agent functionality."""

from src.agent.core import Agent  # pylint: disable=no-name-in-module


def test_agent_initialization():
    """Test agent initializes with correct repository info."""
    test_repo_path = "/test/path"
    agent = Agent()
    agent.initialize(test_repo_path)

    assert "path" in agent.repository_info
    assert agent.repository_info["path"] == test_repo_path
