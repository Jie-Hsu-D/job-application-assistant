import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic()

message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "用一句话跟我打个招呼,证明你能正常回复。"}
    ],
)

print(message.content[0].text)