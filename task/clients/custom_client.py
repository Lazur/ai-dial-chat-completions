import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class CustomDialClient(BaseClient):
    _endpoint: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        # Create headers with api-key and Content-Type
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        
        # Create request data with messages
        request_data = {
            "messages": [msg.to_dict() for msg in messages]
        }
        
        # Debug: print request
        # print(f"[DEBUG] Request to: {self._endpoint}")
        # print(f"[DEBUG] Request body: {json.dumps(request_data, indent=2)}")
        
        # Make POST request
        response = requests.post(self._endpoint, headers=headers, json=request_data)
        
        # Check for errors
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        # Debug: print response
        response_json = response.json()
        print(f"[DEBUG] Response: {json.dumps(response_json, indent=2)}")
        
        # Get content from response
        content = response_json["choices"][0]["message"]["content"]
        print(content)
        return Message(Role.AI, content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        # Create headers with api-key and Content-Type
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        
        # Create request data with stream enabled and messages
        request_data = {
            "stream": True,
            "messages": [msg.to_dict() for msg in messages]
        }
        
        # Debug: print request
        # print(f"[DEBUG] Streaming request to: {self._endpoint}")
        # print(f"[DEBUG] Request body: {json.dumps(request_data, indent=2)}")
        
        # Create empty list to store content snippets
        contents = []
        
        # Use aiohttp session for async streaming
        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, json=request_data, headers=headers) as response:
                # Read response line by line (SSE format)
                async for line in response.content:
                    line = line.decode("utf-8").strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Debug: print raw chunk
                    # print(f"[DEBUG] Raw chunk: {line}")
                    
                    # Check if line starts with "data: "
                    if line.startswith("data: "):
                        data = line[6:]  # Strip "data: " prefix (6 chars)
                        
                        # Skip the final [DONE] marker
                        if data == "[DONE]":
                            continue
                        
                        # Parse JSON and extract content
                        chunk_json = json.loads(data)
                        if chunk_json.get("choices") and chunk_json["choices"][0].get("delta"):
                            content = chunk_json["choices"][0]["delta"].get("content", "")
                            if content:
                                print(content, end="", flush=True)
                                contents.append(content)
        
        # Print empty row (end of streaming)
        print()
        
        # Return Message with collected content
        return Message(Role.AI, "".join(contents))

