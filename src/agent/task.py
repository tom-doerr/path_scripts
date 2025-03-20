#!/usr/bin/env python3
"""Task execution functionality."""

import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from src.utils.xml_tools import extract_xml_from_response, format_xml_response
from src.agent.plan import check_dependencies, apply_plan_updates
from src.utils.feedback import DopamineReward


def execute_task(agent, task_id: str) -> str:
    """
    Execute a specific task from the plan.

    Args:
        agent: The agent instance
        task_id: The ID of the task to execute

    Returns:
        Formatted XML response with execution results
    """
    if not hasattr(agent, 'plan_tree') or not agent.plan_tree:
        return format_xml_response({"error": "No plan exists"})

    try:
        # Parse the plan tree
        root = ET.fromstring(agent.plan_tree)

        # Find the task with the given ID
        task_element = root.find(f".//task[@id='{task_id}']")
        if task_element is None:
            return format_xml_response({"error": f"Task {task_id} not found"})

        # Return basic task info
        return format_xml_response({
            "task": {
                "id": task_id,
                "description": task_element.get("description", ""),
                "status": task_element.get("status", "pending")
            }
        })

    except Exception as e:
        return format_xml_response({"error": f"Error executing task: {str(e)}"})
        # Parse the plan tree
        root = ET.fromstring(agent.plan_tree)

        # Find the task with the given ID
        task_element = root.find(f".//task[@id='{task_id}']")
        if task_element is None:
            return format_xml_response({"error": f"Task {task_id} not found"})

        # Get task details
        description = task_element.get("description", "")
        current_status = task_element.get("status", "pending")

        # Check if task is already completed
        if current_status == "completed":
            return format_xml_response(
                {
                    "warning": f"Task {task_id} is already marked as completed",
                    "task": {
                        "id": task_id,
                        "description": description,
                        "status": current_status,
                    },
                }
            )

        # Check dependencies
        from agent.plan import check_dependencies

        deps_met, missing_deps = check_dependencies(agent, task_id)
        if not deps_met:
            return format_xml_response(
                {
                    "error": "Dependencies not met",
                    "task": {"id": task_id, "description": description},
                    "missing_dependencies": missing_deps,
                }
            )

        # Update task status to in-progress
        task_element.set("status", "in-progress")
        task_element.set("progress", "10")  # Start with 10% progress
        agent.plan_tree = ET.tostring(root, encoding="unicode")

        print(f"Executing task {task_id}: {description}")
        print("Status updated to: in-progress (10%)")

        # Get parent task information for context
        parent_info = ""
        for potential_parent in root.findall(".//task"):
            for child in potential_parent.findall("./task"):
                if child.get("id") == task_id:
                    parent_id = potential_parent.get("id")
                    parent_desc = potential_parent.get("description")
                    parent_info = f"This task is part of: {parent_id} - {parent_desc}"
                    break
            if parent_info:
                break

        # Generate actions for this task
        prompt = f"""
        I need to execute the following task:
        
        TASK ID: {task_id}
        DESCRIPTION: {description}
        {parent_info}
        
        REPOSITORY INFORMATION:
        {json.dumps(agent.repository_info, indent=2)}
        
        CURRENT PLAN:
        {agent.plan_tree}
        
        Generate the necessary actions to complete this task. The actions should be in XML format:
        
        <actions>
          <action type="create_file" path="example.py">
            # Python code here
          </action>
          <action type="modify_file" path="existing.py">
            <change>
              <original>def old_function():</original>
              <new>def new_function():</new>
            </change>
          </action>
          <action type="run_command" command="pytest tests/test_example.py" />
        </actions>
        
        <!-- XML Schema for Response -->
        <response>
          <!-- Simple message to the user -->
          <message>Your response text here</message>
      
          <!-- Actions to execute -->
          <actions>
            <action type="create_file" path="example.py">
              # Python code here
            </action>
            <action type="modify_file" path="existing.py">
              <change>
                <original>def old_function():</original>
                <new>def new_function():</new>
              </change>
            </action>
            <action type="run_command" command="pytest tests/test_example.py" />
          </actions>
      
          <!-- File edits (search and replace) -->
          <file_edits>
            <edit path="path/to/file.py">
              <search>def old_function():</search>
              <replace>def new_function():</replace>
            </edit>
          </file_edits>
      
          <!-- Shell commands -->
          <shell_commands>
            <command safe_to_autorun="true">echo "Hello World"</command>
            <command safe_to_autorun="false">rm -rf some_directory</command>
          </shell_commands>
      
          <!-- Memory updates -->
          <memory_updates>
            <edit>
              <search>Old information to replace</search>
              <replace>Updated information</replace>
            </edit>
            <add>New information to remember</add>
          </memory_updates>
      
          <!-- Execution status -->
          <execution_status complete="true|false" needs_user_input="true|false">
            <message>Status message explaining what's done or what's needed</message>
          </execution_status>
      
          <!-- Plan updates -->
          <plan_update>
            <add_task parent_id="task1" id="task1.3" description="New subtask" status="pending" complexity="medium" depends_on="" progress="0" />
            <modify_task id="task2" description="Updated description" />
            <remove_task id="task3" />
          </plan_update>
        </response>
        
        Think step by step about what needs to be done to complete this task.
        Focus on creating actions that are specific, concrete, and directly implement the task.
        """

        # Update progress to 30% - planning phase
        task_element.set("progress", "30")
        agent.plan_tree = ET.tostring(root, encoding="unicode")
        print("Progress updated to: 30% (planning phase)")

        response = agent.stream_reasoning(prompt)

        # Update progress to 50% - actions generated
        task_element.set("progress", "50")
        agent.plan_tree = ET.tostring(root, encoding="unicode")
        print("Progress updated to: 50% (actions generated)")

        # Extract actions XML from the response
        actions_xml = extract_xml_from_response(response, "actions")
        plan_update_xml = extract_xml_from_response(response, "plan_update")

        # Apply plan updates if present
        if plan_update_xml:
            from agent.plan import apply_plan_updates

            apply_plan_updates(agent, plan_update_xml)

        if not actions_xml:
            # Update task status to failed
            task_element.set("status", "failed")
            task_element.set("notes", "Failed to generate actions")
            task_element.set("progress", "0")
            agent.plan_tree = ET.tostring(root, encoding="unicode")
            print(f"Task {task_id} failed: Could not generate actions")

            # Generate dopamine reward for failure
            if hasattr(agent, "dopamine_reward"):
                dopamine = agent.dopamine_reward.generate_reward(30)
            else:
                from utils.feedback import DopamineReward

                agent.dopamine_reward = DopamineReward(agent.console)
                dopamine = agent.dopamine_reward.generate_reward(30)

            return format_xml_response(
                {
                    "error": "Failed to generate actions for task",
                    "task": {
                        "id": task_id,
                        "description": description,
                        "status": "failed",
                    },
                    "dopamine": dopamine,
                }
            )

        # Update progress to 70% - ready for execution
        task_element.set("progress", "70")
        agent.plan_tree = ET.tostring(root, encoding="unicode")
        print("Progress updated to: 70% (ready for execution)")

        # Generate dopamine reward for successful action generation
        if hasattr(agent, "dopamine_reward"):
            dopamine = agent.dopamine_reward.generate_reward(75)
        else:
            from utils.feedback import DopamineReward

            agent.dopamine_reward = DopamineReward(agent.console)
            dopamine = agent.dopamine_reward.generate_reward(75)

        return format_xml_response(
            {
                "task": {
                    "id": task_id,
                    "description": description,
                    "progress": "70",
                },
                "actions": actions_xml,
                "plan_update": plan_update_xml if plan_update_xml else None,
                "dopamine": dopamine,
            }
        )

    except Exception as e:
        return format_xml_response({"error": f"Error executing task: {str(e)}"})

            # Generate dopamine reward for failure
            if hasattr(agent, "dopamine_reward"):
                dopamine = agent.dopamine_reward.generate_reward(30)
            else:
                from utils.feedback import DopamineReward

                agent.dopamine_reward = DopamineReward(agent.console)
                dopamine = agent.dopamine_reward.generate_reward(30)

            return format_xml_response(
                {
                    "error": "Failed to generate actions for task",
                    "task": {
                        "id": task_id,
                        "description": description,
                        "status": "failed",
                    },
                    "dopamine": dopamine,
                }
            )

    except Exception as e:
        return format_xml_response({"error": f"Error executing task: {str(e)}"})
