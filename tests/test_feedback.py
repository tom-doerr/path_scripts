"""Tests for feedback functionality."""

from src.utils.feedback import DopamineReward
from rich.console import Console

def test_dopamine_reward():
    """Test basic dopamine reward generation."""
    console = Console()
    reward = DopamineReward(console)
    
    # Test with quality score
    result = reward.generate_reward(95)
    assert "DOPAMINE SURGE" in result
    assert "🌟" in result
    
    # Test without quality score (should use last score)
    result2 = reward.generate_reward()
    assert result2  # Should return something
    
    # Test reward for XML response
    response = "<response><message>Test response</message></response>"
    observation = "This is great work! Perfect solution!"
    result3 = reward.reward_for_xml_response(response, observation)
    assert "DOPAMINE" in result3
