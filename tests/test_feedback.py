"""Tests for feedback functionality."""

from rich.console import Console
from src.utils.feedback import DopamineReward


def test_high_quality_reward():
    """Test reward generation for high quality scores."""
    reward = DopamineReward(Console())
    result = reward.generate_reward(95)
    assert "DOPAMINE SURGE" in result
    assert "🌟" in result


def test_medium_quality_reward():
    """Test reward generation for medium quality scores."""
    reward = DopamineReward(Console())
    result = reward.generate_reward(75)
    assert "DOPAMINE BOOST" in result
    assert "😊" in result


def test_low_quality_reward():
    """Test reward generation for low quality scores."""
    reward = DopamineReward(Console())
    result = reward.generate_reward(30)
    assert "DOPAMINE DIP" in result
    assert "😕" in result


def test_default_reward():
    """Test reward generation without quality score."""
    reward = DopamineReward(Console())
    # First call with score to set last_score
    reward.generate_reward(80)
    # Second call without score
    result = reward.generate_reward()
    assert result  # Should return something based on last_score
    assert "DOPAMINE" in result


def test_xml_response_positive_feedback():
    """Test reward generation for positive XML response feedback."""
    reward = DopamineReward(Console())
    response = "<response><message>Test</message></response>"
    result = reward.reward_for_xml_response(response, "Great work! This is excellent!")
    assert "DOPAMINE" in result
    assert "SURGE" in result or "BOOST" in result


def test_xml_response_negative_feedback():
    """Test reward generation for negative XML response feedback."""
    reward = DopamineReward(Console())
    response = "<response><message>Test</message></response>"
    result = reward.reward_for_xml_response(response, "This is bad and wrong")
    assert "DOPAMINE" in result
    assert "DIP" in result or "LOW" in result


def test_xml_response_neutral_feedback():
    """Test reward generation for neutral XML response feedback."""
    reward = DopamineReward(Console())
    response = "<response><message>Test</message></response>"
    result = reward.reward_for_xml_response(response, "This is okay")
    assert "DOPAMINE" in result
    assert "NEUTRAL" in result or "TRICKLE" in result
