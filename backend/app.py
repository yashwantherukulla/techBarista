from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

from getpass import getpass

# Get the personal access token from the user
token = ''

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



if __name__ == '__main__':
    app.run(debug=True)