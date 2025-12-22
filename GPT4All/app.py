from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key="your_api_key",
    base_url='http://localhost:4891/v1'
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

@app.route('/api/completion', methods=['POST'])
def completion():
    data = request.json
    prompt = data['prompt']
    completion = get_completion(prompt)
    return jsonify({'completion': completion})

if __name__ == '__main__':
    app.run()



#   DOS 测试
#   curl -X POST -H "Content-Type: application/json" -d "{\"prompt\": \"3661秒是几小时几分钟几秒啊，\"}" http://localhost:5000/api/completion