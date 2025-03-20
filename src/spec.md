- no actions visible under the model suggests the following actions
- don't think we need an action xml tag, all of those are kind of actions


### Project Initialization
- Write a `spec.md` for each project to define requirements.
- Use `aider` to generate structured output based on the spec.

### Task Management
- Split tasks into small, manageable pieces to increase success rates.
- Use `pytest` for testing and to identify failures.
- Include feedback from test results in prompts for better coordination.

### Monitoring and Coordination
- Use `tmux` for session management, starting new sessions with custom endings to avoid conflicts.
- Display and refresh stats constantly for easy monitoring.
- Coordinate with `agent-aider-worktree` without modifying it to preserve its integrity.

### Planning and Execution
- Create a plan tree using XML to structure tasks.
- Execute tasks based on the generated plan.
- Track task dependencies and show progress.
- Allow the agent to modify its own plan as needed.
- Enable the agent to indicate task completion or request further input from the user.

### User Interaction
- Implement an interactive mode with chat functionality for direct user interaction.
- Require user confirmation for critical actions to ensure control.
- Handle multi-line inputs properly to process pasted content effectively.

### Technical Implementation
- Stream and display reasoning with proper formatting for transparency.
- Manage terminal output to preserve history and avoid overwriting existing text.
- Integrate with different models and APIs for flexibility.
- Use `deepseekr1` for reasoning and evaluation of results.
- Handle API overload issues, possibly by using native DeepSeek APIs when necessary.

### Code Maintenance
- Keep complexity low to ensure maintainability.
- Refactor code into smaller, independent modules for easier testing and development.
- Fix bugs related to API overload and module imports.
- Avoid modifying existing code like `agent-aider-worktree`; duplicate functionality if needed.

### Enhancements
- Include system information (e.g., date, time, timezone) in the context for better awareness.
- Implement multi-step execution to handle complex tasks over multiple interactions.
- Maintain conversation history to provide context for the agent.
- Add a vim-like interface for command navigation (e.g., using `j`, `k` to move through commands).
- Implement persistent memory for the agent to retain and modify information over time.
- Allow the agent to edit files using XML tags (e.g., search and replace with filename specifications).
- Enable the agent to update its plan based on new information learned during execution.

### Context Management
- Format input messages to the model in XML to set a consistent example.
- Provide an XML schema for the agent’s responses to clarify expected output structure.
- Exclude reasoning tokens from the model’s context to avoid confusion, as they weren’t part of training.
- Truncate shell command outputs to the last 5000 characters per command to manage context size.
- Log command execution details (e.g., auto-run, confirmed, rejected) for valuable context.

### Debugging
- Print the complete message sent to the model for debugging purposes.
- Remove unnecessary status messages (e.g., "generating plan", "end of reasoning") and rely on color-coding.

### Alternative Approaches
- Explore using `litellm` with `deepseekr1` as an alternative to `aider` for building the agent.

