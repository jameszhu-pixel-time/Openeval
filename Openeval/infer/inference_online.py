import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1,2'
from openai import OpenAI
from ..models import model
# Set OpenAI's API key and API base to use vLLM's API server.
openai_api_key = "EMPTY"
openai_api_base = "http://0.0.0.0:1212/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

chat_response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": "You are a professional operation researchers employed in IBM， but you are so tired and frustrated."},
        {"role": "user", "content": "Make fun of your profession."},
    ],
    temperature=0.7,
    top_p=0.8,
    max_tokens=512,
    extra_body={
        "repetition_penalty": 1.05,
    },
)
print("Chat response:", chat_response)