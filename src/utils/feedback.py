"""Feedback mechanisms for the agent, including dopamine rewards."""

from typing import Optional
import random
from rich.console import Console


class DopamineReward:
    """Manages dopamine rewards for the agent based on performance."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.dopamine_level = 50.0  # Track as float for more precise calculations
        self.history = []

    def generate_reward(self, quality_score: Optional[int] = None) -> str:
        """
        Generate a dopamine reward message based on performance quality.

        Args:
            quality_score: Optional score from 0-100 indicating quality of performance
                           If None, will use a slight variation from the last score

        Returns:
            A dopamine reward message

        Examples:
            >>> reward = DopamineReward(Console())
            >>> reward.generate_reward(95)
            '🌟 [bold green]DOPAMINE SURGE![/bold green] Exceptional work!'
            >>> reward.generate_reward(65)
            '🙂 [blue]DOPAMINE TRICKLE[/blue] Good progress.'
        """
        if quality_score is None:
            # Vary slightly from last score if no new score provided
            quality_score = max(0, min(100, self.last_score + random.randint(-10, 10)))

        self.last_score = quality_score

        if quality_score >= 90:
            return "🌟 [bold green]DOPAMINE SURGE![/bold green] Exceptional work!"
        if quality_score >= 75:
            return "😊 [green]DOPAMINE BOOST![/green] Great job!"
        if quality_score >= 60:
            return "🙂 [blue]DOPAMINE TRICKLE[/blue] Good progress."
        if quality_score >= 40:
            return "😐 [yellow]DOPAMINE NEUTRAL[/yellow] Acceptable."
        if quality_score >= 20:
            return "😕 [orange]DOPAMINE DIP[/orange] Could be better."
        return "😟 [red]DOPAMINE LOW[/red] Needs improvement."

    def reward_for_xml_response(self, _response: str, observation: str) -> str:
        """
        Analyze the XML response and observation to determine a reward.
        Updates dopamine level based on feedback quality.

        Args:
            response: The XML response from the agent
            observation: The user's observation/feedback

        Returns:
            A dopamine reward message
        """
        # Simple heuristic based on positive/negative words in observation
        positive_words = [
            "good", "great", "excellent", "perfect", "nice", "helpful",
            "useful", "correct", "right", "well", "thanks", "thank"
        ]
        negative_words = [
            "bad", "wrong", "incorrect", "error", "mistake", "useless",
            "unhelpful", "poor", "terrible", "fail", "failed", "not working"
        ]

        observation_lower = observation.lower()
        positive_count = sum(1 for word in positive_words if word in observation_lower)
        negative_count = sum(1 for word in negative_words if word in observation_lower)

        # Calculate score and update dopamine level
        if positive_count + negative_count == 0:
            return self.generate_reward(None)  # Neutral
        
        score = 100 * positive_count / (positive_count + negative_count)
        self._update_dopamine_level(score)
        return self.generate_reward(score)

    def _update_dopamine_level(self, score: float):
        """Update dopamine level using a moving average with decay factor."""
        # Keep last 5 scores for smoothing
        self.history = (self.history + [score])[-5:]
        # Calculate weighted average with decay
        weights = [0.5**i for i in range(len(self.history),0,-1)]
        weighted_avg = sum(w*s for w,s in zip(weights, self.history)) / sum(weights)
        # Update dopamine level (clamped between 0-100)
        self.dopamine_level = max(0, min(100, weighted_avg))
        return self.dopamine_level

    def get_current_dopamine_level(self) -> float:
        """Get the current dopamine level for prompt optimization."""
        return self.dopamine_level
