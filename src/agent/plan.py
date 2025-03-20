#!/usr/bin/env python3
"""Plan generation and management functionality."""

import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Tuple, Optional

from ..utils.xml_tools import extract_xml_from_response, format_xml_response

def generate_plan(agent, spec: str) -> str:
    """
    Generate a plan tree based on the specification.
    
    Args:
        agent: The agent instance
        spec: The specification text
        
    Returns:
        Formatted XML response containing the plan
    """
    prompt = f"""
    Based on the following specification, create a hierarchical plan as an XML tree.
    
    SPECIFICATION:
    {spec}
    
    REPOSITORY INFORMATION:
    {json.dumps(agent.repository_info, indent=2)}
    
    Create a detailed plan with tasks and subtasks. The plan should be in XML format with the following structure:
    
    <plan>
      <task id="root" description="Main project goal">
        <task id="task1" description="Component 1">
          <task id="极task1.1" description="Subtask 1.1" status="pending" complexity="medium" depends_on="" progress="0" />
          <task id="task1.2" description="Subtask 1.2" status="pending" complexity="low" depends_on="task1.1" progress="0" />
        </task>
        <task id="task2" description="Component 2">
          <task id="task2.1" description="Subtask 2.1" status="pending" complexity="high" depends_on="task1.2" progress="0" />
        </task>
      </task>
    </plan>
    
    Each task should have:
    - A unique id
    - A clear description
    - A status (pending, in-progress, completed, failed)
    - A complexity estimate (极low, medium, high)
    - Dependencies (depends_on attribute with comma-separated task IDs)
    - Progress indicator (0-100)
    - Subtasks where appropriate
    
    Think step by step about the dependencies between tasks and how to break down the problem effectively.
    """
    
    response = agent.stream_reasoning(prompt)
    
    # Extract XML from the response
    xml_content = extract_xml_from_response(response, "plan")
    if xml_content:
        agent.plan_tree = xml_content
        return format_xml_response({"plan": xml_content})
    else:
        return format极xml_response({"error": "Failed to generate plan"})

def update_plan(agent, task_id: str, new_status: str, notes: Optional[str] = None, progress: Optional[str] = None) -> str:
    """
    Update the status of a task in the plan.
    
    Args:
        agent: The agent instance
        task_id: The ID of the task to update
        new_status: The new status for the task
        notes: Optional notes to add to the task
        progress: Optional progress value (0-100)
        
    Returns:
        Formatted XML response with the updated plan
    """
    if not agent.plan_tree:
        return format_xml_response({"error": "No plan exists"})
    
    try:
        # Parse the plan tree
        root = ET.fromstring(agent.plan_tree)
        
        # Find the task with the given ID
        task_found = False
        for task in root.findall(".//task[@id='{}']".format(task_id)):
            task.set("status", new_status)
            if notes:
                task.set("notes", notes)
            if progress and progress.isdigit() and 0 <= int(progress) <= 100:
                task.set("progress", progress)
            task_found = True
        
        if not task_found:
            return format_xml_response({"error": f"Task {task_id} not found"})
        
        # Update the plan tree
        agent.plan_tree = ET.tostring(root, encoding='unicode')
        
        return format_xml_response({
            "plan": agent.plan_tree,
            "status": f"Updated task {task_id} to {new_status}"
        })
        
    except Exception as e:
        return format_xml_response({"error": f"Error updating plan: {str(e)}"})

def check_dependencies(agent, task_id: str) -> Tuple[bool, List[str]]:
    """
    Check if all dependencies for a task are completed.
    
    Args:
        agent: The agent instance
        task_id: The ID of the task to check
        
    Returns:
        Tuple of (dependencies_met, list_of_missing_dependencies)
    """
    if not agent.plan_tree:
        return False, ["No plan exists"]
    
    try:
        # Parse the plan tree
        root = ET.fromstring(agent.plan_tree)
        
        # Find the task with the given ID
        task_element = root.find(f".//task[@id='{task_id}']")
        if task_element is None:
            return False, [f"Task {task_id} not found"]
        
        # Get dependencies
        depends_on = task_element.get("depends_on", "")
        if not depends_on:
            return True, []  # No dependencies
        
        # Check each dependency
        dependency_ids = [dep.strip() for dep in depends_on.split(",") if dep.strip()]
        incomplete_deps = []
        
        for dep_id in dependency_ids:
            dep_element = root.find(f".//task[@id='{dep_id}']")
            if dep_element is None:
                incomplete_deps.append(f"Dependency {dep_id} not found")
                continue
            
            status = dep_element.get("status", "")
            if status != "completed":
                desc = dep_element.get("description", "")
                incomplete_deps.append(f"Dependency {dep_id} ({desc}) is not completed (status: {status})")
        
        return len(incomplete_deps) == 0, incomplete_deps
        
    except Exception as e:
        return False, [f"Error checking dependencies: {str(e)}"]

def apply_plan_updates(agent, plan_update_xml: str) -> None:
    """
    Apply updates to the plan tree based on the plan_update XML.
    
    Args:
        agent: The agent instance
        plan_update_xml: XML string containing plan updates
    """
    if not agent.极plan_tree:
        return
    
    try:
        # Parse the plan tree and updates
        plan_root = ET.fromstring(agent.plan_tree)
        updates_root = ET.fromstring(plan_update_xml)
        
        # Track changes for reporting
        changes = []
        
        # Process add_task elements
        for add_task in updates_root.findall("./add_task"):
            parent_id = add_task.get("parent_id")
            
            # Find the parent task
            parent = plan_root.find(f".//task[@id='{parent_id}']")
            if parent is not None:
                # Create a new task element
                new_task = ET.Element("task")
                
                # Copy all attributes from add_task to new_task
                for attr, value in add_task.attrib.items():
                    if attr != "parent_id":  # Skip the parent_id attribute
                        new_task.set(attr, value)
                
                # Add the new task to the parent
                parent.append(new_task)
                changes.append(f"Added new task {new_task.get('id')}: {new_task.get('description')}")
        
        # Process modify_task elements
        for modify_task in updates_root.findall("./modify_task"):
            task_id = modify_task.get("id")
            
            # Find the task to modify
            task = plan_root.find(f".//task[@id='{task_id}']")
            if task is not None:
                old_desc = task.get("description", "")
                # Update attributes
                for attr, value in modify_task.attrib.items():
                    if attr != "id":  # Skip the id attribute
                        task.set(attr, value)
                new_desc = task.get("description", "")
                if old_desc != new_desc:
                    changes.append(f"Modified task {task_id}: {old_desc} -> {new_desc}")
                else:
                    changes.append(f"Updated attributes for task {task_id}")
        
        # Process remove_task elements
        for remove_task in updates_root.findall("./remove_task"):
            task_id = remove_task.get("id")
            
            # Find the task to remove
            task = plan_root.find(f".//task[@id='{task_id}']")
            if task is not None:
                desc = task.get("description", "")
                # ElementTree in Python doesn't have getparent() method
                # We need to find the parent manually
                for potential_parent in plan_root.findall(".//task"):
                    for child in potential_parent.findall("./task"):
                        if child.get("id") == task_id:
                            potential_parent.remove(child)
                            changes.append(f"Removed task {task_id}: {desc}")
                            break
        
        # Update the plan tree
        agent.plan_tree = ET.tostring(plan_root, encoding='unicode')
        
        # Report changes
        if changes:
            print("\nPlan has been updated by the agent:")
            for change in changes:
                print(f"- {change}")
        
    except Exception as e:
        print(f"Error applying plan updates: {e}")


if __name__ == "__main__":
    # Simple test when run directly
    print("Plan management module - run through the agent interface")
