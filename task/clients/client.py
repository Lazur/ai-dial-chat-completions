from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        # Create Dial client for synchronous requests
        self._client = Dial(api_key=self._api_key, base_url=DIAL_ENDPOINT)
        # Create AsyncDial client for asynchronous streaming requests
        self._async_client = AsyncDial(api_key=self._api_key, base_url=DIAL_ENDPOINT)

    def get_completion(self, messages: list[Message]) -> Message:
        # Create chat completions with sync client
        response = self._client.chat.completions.create(
            deployment_name=self._deployment_name,
            messages=[msg.to_dict() for msg in messages]
        )
        
        # Check if choices are present
        if not response.choices:
            raise Exception("No choices in response found")
        
        # Get content from response, print it and return message
        content = response.choices[0].message.content
        print(content)
        return Message(Role.AI, content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        # Create chat completions with async client (streaming enabled)
        response = await self._async_client.chat.completions.create(
            deployment_name=self._deployment_name,
            messages=[msg.to_dict() for msg in messages],
            stream=True
        )
        
        # Collect all content chunks
        contents = []
        
        # Async loop through chunks
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                contents.append(content)
        
        # Print empty row (end of streaming)
        print()
        
        # Return Message with collected content
        return Message(Role.AI, "".join(contents))
