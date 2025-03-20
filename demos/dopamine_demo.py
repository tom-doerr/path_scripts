from rich.console import Console
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from src.utils.feedback import DopamineReward

def demo_dopamine_optimization():
    """Demo dopamine-based prompt optimization"""
    console = Console()
    reward = DopamineReward(console)
    
    # Initial state
    console.print(f"\nStarting dopamine level: {reward.dopamine_level:.1f}")
    
    # Simulate positive interaction
    console.print("\n[bold]Test 1: Positive feedback[/bold]")
    feedback = reward.reward_for_xml_response("", "Perfect! Exactly what I needed!")
    console.print(f"Reward: {feedback}")
    console.print(f"New dopamine level: {reward.dopamine_level:.1f}")
    
    # Simulate negative interaction
    console.print("\n[bold]Test 2: Negative feedback[/bold]")
    feedback = reward.reward_for_xml_response("", "Wrong! This is completely incorrect.")
    console.print(f"Reward: {feedback}")
    console.print(f"New dopamine level: {reward.dopamine_level:.1f}")
    
    # Simulate mixed interaction
    console.print("\n[bold]Test 3: Mixed feedback[/bold]")
    feedback = reward.reward_for_xml_response("", "Partially correct but needs improvement")
    console.print(f"Reward: {feedback}")
    console.print(f"New dopamine level: {reward.dopamine_level:.1f}")

if __name__ == "__main__":
    demo_dopamine_optimization()
