# # Import LangChain's memory module for storing conversation history
# from langchain.memory import ConversationBufferMemory


# # ------------------------------------------------------------
# # Shared memory initialization
# # ------------------------------------------------------------
# # Create a single shared memory buffer instance that stores conversation history
# # - memory_key: identifies how the memory is referenced across agents
# # - return_messages=True: keeps full message objects instead of plain text
# _shared_memory = ConversationBufferMemory(
#     memory_key="chat_history",
#     return_messages=True,
# )

# # Max number of recent message pairs (input+output) to keep in memory.
# # Prevents context from growing too large for the LLM's token limit.
# MAX_MEMORY_PAIRS = 3


# # ------------------------------------------------------------
# # Get shared memory instance
# # ------------------------------------------------------------
# # Purpose: Provides global access to the same memory object used by all agents.
# # Ensures that all agents (symptom, lifestyle, etc.) share a consistent conversation state.
# def get_shared_memory() -> ConversationBufferMemory:
#     return _shared_memory


# def trim_memory():
#     """Keep only the most recent MAX_MEMORY_PAIRS exchanges to avoid token limit errors."""
#     messages = _shared_memory.chat_memory.messages
#     # Each pair = 2 messages (HumanMessage + AIMessage)
#     max_messages = MAX_MEMORY_PAIRS * 2
#     if len(messages) > max_messages:
#         _shared_memory.chat_memory.messages = messages[-max_messages:]


# def reset_memory():
#     _shared_memory.clear()


# This is by anti gravity

# ------------------------------------------------------------
# Shared memory initialization
# ------------------------------------------------------------
# Create a single shared memory buffer instance that stores conversation history
# - memory_key: identifies how the memory is referenced across agents
# - return_messages=True: keeps full message objects instead of plain text

# Import LangChain's memory module for storing conversation history
from langchain.memory import ConversationBufferMemory
_shared_memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
)
# Max number of recent message pairs (input+output) to keep in memory.
# Prevents context from growing too large for the LLM's token limit.
MAX_MEMORY_PAIRS = 3
# ------------------------------------------------------------
# Get shared memory instance
# ------------------------------------------------------------
# Purpose: Provides global access to the same memory object used by all agents.
# Ensures that all agents (symptom, lifestyle, etc.) share a consistent conversation state.
def get_shared_memory() -> ConversationBufferMemory:
    return _shared_memory
def trim_memory():
    """Keep only the most recent MAX_MEMORY_PAIRS exchanges to avoid token limit errors."""
    messages = _shared_memory.chat_memory.messages
    # Each pair = 2 messages (HumanMessage + AIMessage)
    max_messages = MAX_MEMORY_PAIRS * 2
    if len(messages) > max_messages:
        _shared_memory.chat_memory.messages = messages[-max_messages:]
def reset_memory():
    _shared_memory.clear()
