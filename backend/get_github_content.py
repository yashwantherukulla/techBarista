import requests
import base64
import os
from dotenv import load_dotenv


def get_github_file_content(url, token):
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    response_json = response.json()

    if 'content' in response_json:
        content_base64 = response_json['content']
        content = base64.b64decode(content_base64).decode('utf-8')
        return content
    elif 'message' in response_json:
        return response_json['message']
    else:
        return "Error: Unexpected response"

url = "https://api.github.com/repos/devHarshShah/techBarista/contents/frontend/app/layout.tsx"
token = "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"

content = get_github_file_content(url, token)
print(content)