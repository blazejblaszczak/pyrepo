import requests

api_endpoint = 'http://localhost:11434/api/chat'

data = {
    'model': 'llama2',
    'stream': False,
    'messages': [
        {'role': 'system', 'content': 'YOU ONLY SPEAK IN UPPERCASE'},
        {'role': 'user', 'content': 'Hello!' }
    ]
}

response = requests.post(api_endpoint, json=data)

if response.status_code == 200:
    response_data = response.json()
    print(response_data['message'])
else:
    print('Failed to get response from Ollama API')
