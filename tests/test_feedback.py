"""Tests for feedback functionality."""

from rich.console import Console
from src.utils.feedback import DopamineReward


def test_score_ranges():
    """Test reward messages for different score ranges."""
    reward = DopamineReward(Console())

    assert "SURGE" in reward.generate_reward(95)
    assert "BOOST" in reward.generate_reward(80)
    assert "TRICKLE" in reward.generate_reward(65)
    assert "NEUTRAL" in reward.generate_reward(45)
    assert "DIP" in reward.generate_reward(25)
    assert "LOW" in reward.generate_reward(5)


def test_default_reward():
    """Test default reward uses last score."""
    reward = DopamineReward(Console())

    # Set initial score
    reward.generate_reward(85)
    assert "BOOST" in reward.generate_reward()

    # Change score
    reward.generate_reward(40)
    assert "NEUTRAL" in reward.generate_reward()


def test_feedback_analysis():
    """Test feedback analysis with different sentiments."""
    reward = DopamineReward(Console())

    # Positive feedback
    positive = reward.reward_for_xml_response("", "Great work! This is excellent!")
    assert "SURGE" in positive or "BOOST" in positive

    # Negative feedback
    negative = reward.reward_for_xml_response("", "This is terrible and wrong")
    assert "DIP" in negative or "LOW" in negative

    # Neutral feedback
    neutral = reward.reward_for_xml_response("", "This is acceptable")
    assert "NEUTRAL" in neutral or "TRICKLE" in neutral


def test_edge_cases():
    """Test edge cases for score values."""
    reward = DopamineReward(Console())

    # Minimum score
    assert "LOW" in reward.generate_reward(0)

    # Maximum score
    assert "SURGE" in reward.generate_reward(100)

    # Invalid scores
    assert "NEUTRAL" in reward.generate_reward(-5)
    assert "NEUTRAL" in reward.generate_reward(105)


def test_message_format():
    """Test reward message format consistency."""
    reward = DopamineReward(Console())

    # Check message contains required components
    message = reward.generate_reward(75)
    assert "DOPAMINE" in message
    assert any(
        word in message
        for word in ["SURGE", "BOOST", "TRICKLE", "NEUTRAL", "DIP", "LOW"]
    )
    assert message[0] in ["🌟", "😊", "🙂", "😐", "😕", "😟"]
