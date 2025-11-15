import os
import requests
from dotenv import dotenv_values
values = dotenv_values('LLM Integration/.env')
key = values['OPEN_ROUTER_API_KEY']
headers = {
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'HTTP-Referer': 'https://github.com/betoq/exchange-programming',
    'X-Title': 'Exchange Programming'
}
payload = {'model':'deepseek/deepseek-r1-0528-qwen3-8b:free','messages':[{'role':'user','content':'hello'}]}
response = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=payload, timeout=60)
print('status', response.status_code)
print(response.text)
print('request headers', response.request.headers)
