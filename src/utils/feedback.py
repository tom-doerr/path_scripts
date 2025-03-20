"""Feedback mechanisms for the agent, including dopamine rewards."""

from typing import Dict, Any, Optional
import random
from rich.console import Console

class DopamineReward:
    """Manages dopamine rewards for the agent based on performance."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.last_score = 50  # Neutral starting point
        
    def generate_reward(self, quality_score: Optional[int] = None) -> str:
        """
        Generate a dopamine reward message based on performance quality.
        
        Args:
            quality_score: Optional score from 0-100 indicating quality of performance
                           If None, will use a slight variation from the last score
                           
        Returns:
            A dopamine reward message
        """
        if quality_score is None:
            # Vary slightly from last score if no new score provided
            quality_score = max(0, min(100, self.last_score + random.randint(-10, 10)))
        
        self.last_score = quality_score
        
        if quality_score >= 90:
            return "🌟 [bold green]DOPAMINE SURGE![/bold green] Exceptional work!"
        elif quality_score >= 75:
            return "😊 [green]DOPAMINE BOOST![/green] Great job!"
        elif quality_score >= 60:
            return "🙂 [blue]DOPAMINE TRICKLE[/blue] Good progress."
        elif quality_score >= 40:
            return "😐 [yellow]DOPAMINE NEUTRAL[/yellow] Acceptable."
        elif quality_score >= 20:
            return "😕 [orange]DOPAMINE DIP[/orange] Could be better."
        else:
            return "😟 [red]DOPAMINE LOW[/red] Needs improvement."
    
    def reward_for_xml_response(self, response: str, observation: str) -> str:
        """
        Analyze the XML response and observation to determine a reward.
        
        Args:
            response: The XML response from the agent
            observation: The user's observation/feedback
            
        Returns:
            A dopamine reward message
        """
        # Simple heuristic based on positive/negative words in observation
        positive_words = ["good", "great", "excellent", "perfect", "nice", "helpful", 
                         "useful", "correct", "right", "well", "thanks", "thank"]
        negative_words = ["bad", "wrong", "incorrect", "error", "mistake", "useless", 
                         "unhelpful", "poor", "terrible", "fail", "failed", "not working"]
        
        observation_lower = observation.lower()
        
        # Count positive and negative words
        positive_count = sum(1 for word in positive_words if word in observation_lower)
        negative_count = sum(1 for word in negative_words if word in observation_lower)
        
        # Calculate a simple score
        if positive_count + negative_count == 0:
            # No clear feedback, maintain previous score
            return self.generate_reward(None)
        
        # Calculate percentage of positive words
        score = int(100 * positive_count / (positive_count + negative_count))
        return self.generate_reward(score)
