from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import asyncio
from main import main
app = Flask(__name__)
CORS(app)  

import base64





token = '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'
def get_repo_structure_comb(repo_url, path=''):
    # Extract the owner and repo name from the URL
    owner, repo = repo_url.split('github.com/')[-1].split('/')
    
    # GitHub API URL for the repo contents
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    
    # Send a GET request to GitHub API
    headers = {'Authorization': f'token {token}'}
    response = requests.get(api_url, headers=headers)
    
    # If the request was successful, process the JSON response
    if response.status_code == 200:
        contents = response.json()
        structure = {'name': path.split('/')[-1] if path else repo, 'type': 'dir', 'content': [], 'url': api_url, 'api_url': api_url}
        for item in contents:
            if item['type'] == 'dir':
                # If the item is a directory, fetch its contents recursively
                item_structure = get_repo_structure_comb(repo_url, item['path'])
                structure['content'].append(item_structure)
            else:
                # If the item is a file, add it to the structure
                structure['content'].append({
                    'name': item['name'],
                    'type': 'file',
                    'path': item['path'],
                    'url': item['html_url'],
                    'api_url': api_url,
                    'content': base64.b64decode(item['content']).decode('utf-8') if 'content' in item else None
                })
        return structure
    else:
        return None
# Get the personal access token from the user


def get_repo_structure_clean(repo_url, path=''):
    # Extract the owner and repo name from the URL
    owner, repo = repo_url.split('github.com/')[-1].split('/')
    
    # GitHub API URL for the repo contents
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    
    # Send a GET request to the GitHub API
    headers = {'Authorization': f'token {token}'}
    response = requests.get(api_url, headers=headers)
    
    
    # If the request was successful, process the JSON response
    if response.status_code == 200:
        contents = response.json()
        structure = []
        for item in contents:
            if item['type'] == 'dir':
                # If the item is a directory, fetch its contents recursively
                item_structure = get_repo_structure_clean(repo_url, item['path'])
                
                structure.append({
                    'name': item['name'],
                    'type': 'dir',
                    'contents': item_structure
                })
            else:
                # If the item is a file, add it to the structure
                structure.append({
                    'name': item['name'],
                    'type': 'file'
                })
        return structure
    else:
        return None
    
def get_repo_structure_blob(repo_url, path=''):
    # Extract the owner and repo name from the URL
    owner, repo = repo_url.split('github.com/')[-1].split('/')
    # GitHub API URL for the repo contents
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    # Send a GET request to the GitHub API
    headers = {'Authorization': f'token {token}'}
    response = requests.get(api_url, headers=headers)
    contents = response.json()
    if response.status_code == 200:
        return contents
    else:
        return None

@app.route('/get_structure_clean', methods=['POST'])
def get_structure_clean():
    data = request.get_json()
    repo_url = data['key']
    structure = get_repo_structure_clean(repo_url)
    return {'clean': structure}, 200

@app.route('/get_structure_blob', methods=['POST'])
def get_structure_blob():
    data = request.get_json()
    repo_url = data['key']
    blob = get_repo_structure_blob(repo_url)
    return {'blob':blob}, 200

@app.route('/get_structure_comb', methods=['POST'])
def get_structure_combine():
    data = request.get_json()
    repo_url = data['key']
    blob = get_repo_structure_comb(repo_url)
    return {'blob':blob}, 200

@app.route('/ask_code_llm', methods=['POST'])
def askCode():
    data = request.get_json()
    question = data['query']
    codeurl = data['codeurl']

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(main(question, codeurl))
    loop.close()

    return {'response': response}, 200

@app.route('/summarize_using_llm', methods=['POST'])
def sumCode():
    data = request.get_json()
    question = data['query']
    codeurl = data['codeurl']
    response = main(question, codeurl)
    return {'response': response}, 200

@app.route('/get_file_url', methods=['POST'])
def get_file_url():
    data = request.get_json()
    repo_url = data['repo_url']
    file_path = data['file_path']
    owner, repo = repo_url.split('github.com/')[-1].split('/')
    file_url = f'https://api.github.com/repos/{owner}/{repo}/contents{file_path}'
    return {'file_url': file_url}, 200

if __name__ == '__main__':
    app.run(debug=True, port=8080)