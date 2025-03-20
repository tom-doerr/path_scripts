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
    assert "DOPAMINE LOW" in result
    assert "😟" in result


def test_default_reward():
    """Test reward generation without quality score."""
    reward = DopamineReward(Console())
    # First call with score to set last_score
    reward.generate_reward(80)
    # Second call without score
    result = reward.generate_reward()
    assert result  # Should return something based on last_score


def test_xml_response_reward():
    """Test reward generation for XML responses."""
    reward = DopamineReward(Console())
    response = "<response><message>Test</message></response>"
    
    # Test positive observation
    positive_result = reward.reward_for_xml_response(response, "Great work!")
    assert "DOPAMINE" in positive_result
    
    # Test negative observation
    negative_result = reward.reward_for_xml_response(response, "This is bad")
    assert "DOPAMINE" in negative_result
