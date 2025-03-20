"""Tests for feedback functionality."""

from rich.console import Console
from utils.feedback import DopamineReward

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
    
    # Test boundary scores
    assert "SURGE" in reward.generate_reward(90)
    assert "BOOST" in reward.generate_reward(75)
    assert "TRICKLE" in reward.generate_reward(60)
    assert "NEUTRAL" in reward.generate_reward(40)
    assert "DIP" in reward.generate_reward(20)
    assert "LOW" in reward.generate_reward(10)

def test_random_variation():
    """Test random variation when no score is provided."""
    reward = DopamineReward(Console())
    feedback1 = reward.generate_reward()
    feedback2 = reward.generate_reward()
    assert feedback1 != feedback2  # Should be different due to random variation

def test_feedback_with_unicode():
    """Test feedback handles unicode characters."""
    reward = DopamineReward(Console())
    feedback = reward.reward_for_xml_response("", "Great job! 🎉")
    assert "SURGE" in feedback or "BOOST" in feedback

def test_feedback_with_numbers():
    """Test feedback handles numeric scores."""
    reward = DopamineReward(Console())
    feedback = reward.generate_reward(85)
    assert "SURGE" in feedback or "BOOST" in feedback

def test_feedback_with_long_text():
    """Test feedback handles long text input."""
    reward = DopamineReward(Console())
    long_text = "This is a very long piece of feedback " * 10
    feedback = reward.reward_for_xml_response("", long_text)
    assert any(word in feedback for word in ["SURGE", "BOOST", "TRICKLE", "NEUTRAL", "DIP", "LOW"])
