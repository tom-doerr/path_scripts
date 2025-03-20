"""Tests for feedback functionality."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add src directory to Python path
src_dir = str(Path(__file__).parent.parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from rich.console import Console
from src.utils.feedback import DopamineReward


def test_initial_score():
    """Test initial score is neutral."""
    reward = DopamineReward(Console())
    assert "NEUTRAL" in reward.generate_reward()


def test_positive_feedback():
    """Test strongly positive feedback."""
    reward = DopamineReward(Console())
    feedback = reward.reward_for_xml_response("", "Amazing! Perfect solution!")
    assert "SURGE" in feedback


def test_negative_feedback():
    """Test strongly negative feedback."""
    reward = DopamineReward(Console())
    feedback = reward.reward_for_xml_response("", "This is completely wrong!")
    assert "LOW" in feedback


def test_mixed_feedback():
    """Test feedback with both positive and negative words."""
    reward = DopamineReward(Console())
    feedback = reward.reward_for_xml_response("", "Good effort but needs improvement")
    assert "TRICKLE" in feedback or "NEUTRAL" in feedback


def test_empty_feedback():
    """Test empty feedback string."""
    reward = DopamineReward(Console())
    feedback = reward.reward_for_xml_response("", "")
    assert "NEUTRAL" in feedback


def test_score_boundaries():
    """Test score boundary conditions."""
    reward = DopamineReward(Console())
    
    # Test exact boundary scores
    assert "SURGE" in reward.generate_reward(90)
    assert "BOOST" in reward.generate_reward(75)
    assert "TRICKLE" in reward.generate_reward(60)
    assert "NEUTRAL" in reward.generate_reward(40)
    assert "DIP" in reward.generate_reward(20)
    assert "LOW" in reward.generate_reward(10)
