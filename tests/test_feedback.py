"""Tests for feedback functionality."""

from rich.console import Console
from src.utils.feedback import DopamineReward  # pylint: disable=no-name-in-module


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
    assert "TRICKLE" in feedback  # 65 should be in the TRICKLE range


def test_positive_feedback_edge_case():
    """Test edge case for positive feedback."""
    reward = DopamineReward(Console())
    feedback = reward.generate_reward(75)
    assert "BOOST" in feedback


def test_negative_feedback_edge_case():
    """Test edge case for negative feedback."""
    reward = DopamineReward(Console())
    feedback = reward.generate_reward(39)
    assert "DIP" in feedback


def test_reward_with_positive_observation():
    """Test reward generation with positive user feedback affects dopamine level."""
    reward = DopamineReward(Console())
    initial_level = reward.dopamine_level
    reward.reward_for_xml_response("", "Good job! This is perfect!")
    assert reward.dopamine_level > initial_level


def test_reward_with_negative_observation():
    """Test reward generation with negative user feedback affects dopamine level."""
    reward = DopamineReward(Console())
    initial_level = reward.dopamine_level
    reward.reward_for_xml_response("", "Bad result! Wrong and useless!")
    assert reward.dopamine_level < initial_level


def test_reward_with_neutral_observation():
    """Test reward generation with mixed feedback."""
    reward = DopamineReward(Console())
    feedback = reward.reward_for_xml_response("", "OK but could be better")
    assert "NEUTRAL" in feedback


def test_empty_feedback_defaults_neutral():
    """Test empty feedback defaults to neutral."""
    reward = DopamineReward(Console())
    feedback = reward.reward_for_xml_response("", "")
    assert "NEUTRAL" in feedback


def test_default_reward_score():
    """Test reward generation with default scoring."""
    reward = DopamineReward(Console())
    feedback = reward.generate_reward()
    assert "DOPAMINE" in feedback  # Should handle None score
