"""Tests for feedback functionality."""

from rich.console import Console
from src.utils.feedback import DopamineReward


def test_initial_score_neutral():
    """Test initial score is neutral."""
    reward = DopamineReward(Console())
    assert "NEUTRAL" in reward.generate_reward()


def test_positive_feedback_high_score():
    """Test high score generates positive feedback."""
    reward = DopamineReward(Console())
    feedback = reward.generate_reward(95)
    assert "SURGE" in feedback


def test_negative_feedback_low_score():
    """Test low score generates negative feedback."""
    reward = DopamineReward(Console())
    feedback = reward.generate_reward(15)
    assert "LOW" in feedback


def test_mixed_feedback_mid_score():
    """Test mid-range score generates mixed feedback."""
    reward = DopamineReward(Console())
    feedback = reward.generate_reward(65)
    assert "TRICKLE" in feedback or "BOOST" in feedback


def test_empty_feedback_defaults_neutral():
    """Test empty feedback defaults to neutral."""
    reward = DopamineReward(Console())
    feedback = reward.reward_for_xml_response("", "")
    assert "NEUTRAL" in feedback
