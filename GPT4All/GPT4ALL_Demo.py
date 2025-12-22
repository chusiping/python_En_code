from openai import OpenAI

client = OpenAI(
  api_key="xxx",
  base_url = 'http://localhost:4891/v1'
)


# gpt-3.5-turbo-1106
# gpt4all-13b-snoozy-q4_0
def get_completion(prompt, model="gpt-3.5-turbo-1106"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content

prompt = "3661秒是几小时几分钟几秒啊，"
print(get_completion(prompt))


# 参考 https://wulu.zone/posts/openai-api-py
