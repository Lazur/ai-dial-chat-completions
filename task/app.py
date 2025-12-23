import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    # 1.1. Create DialClient (using aidial-client library)
    # client = DialClient("gpt-4o")
    
    # 1.2. Create CustomDialClient (for testing with raw HTTP requests)
    # Uncomment the line below to test with CustomDialClient instead:
    client = CustomDialClient("gpt-4o")
    
    # 2. Create Conversation object
    conversation = Conversation()
    
    # 3. Get System prompt from console or use default
    print("Provide System prompt or press 'enter' to continue.")
    system_prompt_input = input("> ").strip()
    system_prompt = system_prompt_input if system_prompt_input else DEFAULT_SYSTEM_PROMPT
    
    # Add system message to conversation
    conversation.add_message(Message(Role.SYSTEM, system_prompt))
    
    # 4. Use infinite cycle to get user messages
    while True:
        print("\nType your question or 'exit' to quit.")
        user_input = input("> ").strip()
        
        # 5. If user message is 'exit' then stop the loop
        if user_input.lower() == "exit":
            print("Exiting the chat. Goodbye!")
            break
        
        # Skip empty input
        if not user_input:
            continue
        
        # 6. Add user message to conversation history
        conversation.add_message(Message(Role.USER, user_input))
        
        # 7. Call stream_completion() or get_completion() based on stream param
        print("AI: ", end="", flush=True)
        if stream:
            ai_message = await client.stream_completion(conversation.get_messages())
        else:
            ai_message = client.get_completion(conversation.get_messages())
        
        # 8. Add generated message to history
        conversation.add_message(ai_message)


asyncio.run(
    start(True)
)
