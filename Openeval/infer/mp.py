# 文件顶层
import openai
def generate_mp(prompt, model_path, params_dict, host, port):
    import openai

    openai_api_key = "EMPTY"
    openai_api_base = f"http://{host}:{port}/v1"

    client = openai.OpenAI(api_key=openai_api_key, base_url=openai_api_base)

    n = params_dict.get("n", 1)
    completion = client.chat.completions.create(
        model=model_path,
        messages=[
            {"role": "system", "content": "follow the instruction below"},
            {"role": "user", "content": prompt}
        ],
        temperature=params_dict.get("temperature", 0.7),
        top_p=params_dict.get("top_p", 0.8),
        max_tokens=params_dict.get("max_tokens", 2048),
        extra_body={
            "repetition_penalty": params_dict.get("repetition_penalty", 1.5),
            "presence_penalty": params_dict.get("presence_penalty", 1.2),
        },
        n=n
    )
    return [choice.message.content for choice in completion.choices[:n]]