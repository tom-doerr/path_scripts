  import os
from camel.agents import ChatAgent
from camel.memory import ChatHistoryMemory
from camel.messages import BaseMessage
from camel.models import ModelFactory

# Step 1: Define a function to read files
def read_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")
    with open(file_path, 'r') as file:
        return file.read()

# Step 2: Initialize the CAMEL agent with memory
def create_spec_review_agent():
    # Configure the memory to retain context
    memory = ChatHistoryMemory(window_size=10)  # Retains last 10 messages
    
    # Use OpenAI's GPT-4 as the model (replace with your API key)
    model = ModelFactory.create(model_type="openai", model_config={"api_key": "your_openai_api_key"})
    
    # Initialize the ChatAgent
    agent = ChatAgent(model=model, memory=memory)
    return agent

# Step 3: Function to review specs and code
def review_specs_and_code(agent, spec_file_path, code_file_path):
    # Read the spec and code files
    spec_content = read_file(spec_file_path)
    code_content = read_file(code_file_path)
    
    # Create an instruction message for the agent
    instruction = (
        "You are a code review assistant. Your task is to:\n"
        "1. Review the specifications in the provided spec.md file.\n"
        "2. Analyze the code in the provided main.py file.\n"
        "3. Identify and list any specifications that are violated by the code.\n"
        "Return the result in the format: 'Violations: [list of violated specs]'.\n\n"
        f"Here is the spec content:\n{spec_content}\n\n"
        f"Here is the code content:\n{code_content}"
    )
    
    # Create a user message
    user_msg = BaseMessage.make_user_message(role_name="User", content=instruction)
    
    # Record the message to memory
    agent.record_message(user_msg)
    
    # Generate a response based on the memory context
    response = agent.step()
    
    # Extract the agent's response content
    return response.content

# Step 4: Main execution
def main():
    # File paths (adjust these to your actual file locations)
    spec_file_path = "spec.md"
    code_file_path = "main.py"
    
    # Create the agent
    agent = create_spec_review_agent()
    
    # Review specs and code
    result = review_specs_and_code(agent, spec_file_path, code_file_path)
    
    # Print the result
    print("Agent's Review Result:")
    print(result)
    
    # Optionally, retrieve the memory context for debugging
    context = agent.memory.get_context()
    print("\nMemory Context:")
    print(context)

# Example spec.md content (save this as spec.md)
"""
# Project Specifications
1. The function `add_numbers` must take two parameters: `a` and `b`.
2. The function `add_numbers` must return the sum of `a` and `b`.
3. The code must include a function called `greet_user` that prints "Hello, User!".
"""

# Example main.py content (save this as main.py)
"""
def add_numbers(a, b, c):
    return a + b + c

def say_hello():
    print("Hi there!")
"""

if __name__ == "__main__":
    main()
















 from camel.agents import ChatAgent
from camel.memory import LongtermAgentMemory, ScoreBasedContextCreator
from camel.storage import InMemoryKeyValueStorage, QdrantStorage

# Step 1: Initialize storage backends
chat_history_storage = InMemoryKeyValueStorage()
vector_db_storage = QdrantStorage(path="./vector_db", prefer_grpc=True)

# Step 2: Initialize memory with context creator
memory = LongtermAgentMemory(
    context_creator=ScoreBasedContextCreator(),
    chat_history_block=chat_history_storage,
    vector_db_block=vector_db_storage,
    retrieve_limit=3
)

# Step 3: Initialize the agent with memory
agent = ChatAgent(model="gpt-4", memory=memory)

# Step 4: Retrieve memory context (using retrieve() for LongtermAgentMemory)
context = agent.memory.retrieve()
print("Combined memory context:", context)

# Step 5: Record a new message
new_user_msg = BaseMessage.make_user_message(role_name="User", content="What's the weather like today?")
agent.record_message(new_user_msg)

# Step 6: Retrieve updated context
updated_context = agent.memory.retrieve()
print("Updated combined memory context:", updated_context)
