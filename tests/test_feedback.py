"""Tests for feedback functionality."""

from rich.console import Console
from src.utils.feedback import DopamineReward


def test_reward_score_ranges():
    """Test reward messages for different score ranges."""
    reward = DopamineReward(Console())

    # Test score boundaries
    assert "SURGE" in reward.generate_reward(90)
    assert "BOOST" in reward.generate_reward(75)
    assert "TRICKLE" in reward.generate_reward(60)
    assert "NEUTRAL" in reward.generate_reward(50)
    assert "DIP" in reward.generate_reward(30)
    assert "LOW" in reward.generate_reward(10)


def test_reward_emojis():
    """Test that rewards include appropriate emojis."""
    reward = DopamineReward(Console())

    assert "🌟" in reward.generate_reward(95)
    assert "😊" in reward.generate_reward(75)
    assert "😐" in reward.generate_reward(50)
    assert "😕" in reward.generate_reward(30)
    assert "😟" in reward.generate_reward(10)


def test_default_reward_uses_last_score():
    """Test that default reward uses last score."""
    reward = DopamineReward(Console())

    # Set last score to high
    reward.generate_reward(95)
    assert "SURGE" in reward.generate_reward()

    # Set last score to low
    reward.generate_reward(20)
    assert "DIP" in reward.generate_reward()


def test_xml_feedback_analysis():
    """Test XML feedback analysis with different sentiments."""
    reward = DopamineReward(Console())
    xml = "<response><message>Test</message></response>"

    # Positive feedback
    result = reward.reward_for_xml_response(xml, "This is excellent work!")
    assert "SURGE" in result or "BOOST" in result

    # Negative feedback
    result = reward.reward_for_xml_response(xml, "This is terrible work!")
    assert "DIP" in result or "LOW" in result

    # Neutral feedback
    result = reward.reward_for_xml_response(xml, "This is acceptable")
    assert "NEUTRAL" in result or "TRICKLE" in result


def test_reward_edge_cases():
    """Test edge cases for reward generation."""
    reward = DopamineReward(Console())

    # Minimum score
    assert "LOW" in reward.generate_reward(0)

    # Maximum score
    assert "SURGE" in reward.generate_reward(100)

    # Invalid score
    assert "NEUTRAL" in reward.generate_reward(-10)
    assert "NEUTRAL" in reward.generate_reward(110)
