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
