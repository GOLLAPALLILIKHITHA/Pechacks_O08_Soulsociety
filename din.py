import requests
import base64
import google.generativeai as genai
import streamlit as st

# GitHub API Token (personal access token)
GITHUB_API_TOKEN = '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'
GEMINI_API_KEY = 'AIzaSyBBZ5_9tGyMUYBnLF3qbjUTB_Mfrd7bfm8'

# Configure Gemini API with API key
genai.configure(api_key=GEMINI_API_KEY)

def fetch_github_repos(username):
    url = f'https://api.github.com/users/{username}/repos'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repos = response.json()
        return [repo['full_name'] for repo in repos]
    else:
        st.error(f"Error fetching GitHub repos: {response.status_code}, {response.text}")
        return []

def fetch_readme(repo_full_name):
    url = f'https://api.github.com/repos/{repo_full_name}/contents/README.md'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        readme_content = base64.b64decode(data['content']).decode('utf-8')
        return readme_content
    elif response.status_code == 404:
        st.warning(f"No README.md found for repo {repo_full_name}.")
    else:
        st.error(f"Error fetching README.md: {response.status_code}, {response.text}")
    return None

def fetch_repo_files(repo_full_name):
    url = f'https://api.github.com/repos/{repo_full_name}/contents'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        files = response.json()
        return [file['path'] for file in files if file['type'] == 'file']
    else:
        st.error(f"Error fetching repo files: {response.status_code}, {response.text}")
        return []

def fetch_file_content(repo_full_name, file_path):
    url = f'https://api.github.com/repos/{repo_full_name}/contents/{file_path}'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        return content
    else:
        st.error(f"Error fetching file content: {response.status_code}, {response.text}")
        return None

def chat_with_content(content):
    model = genai.GenerativeModel("gemini-1.5-flash")
    st.write("Chat initialized. Type 'exit' to end the chat.")
    user_input = st.text_input("You:", "")
    while user_input.lower() != 'exit':
        response = model.generate_content(content + "\n\n" + user_input)
        st.write(f"Gemini: {response.text}")
        user_input = st.text_input("You:", "")

def main():
    st.title("GitHub Repo + Gemini Chat Interface")

    github_username = st.text_input("Enter GitHub username: ", "")
    
    if github_username:
        st.write(f"Fetching repositories for: {github_username}")
        repos = fetch_github_repos(github_username)
        
        if repos:
            repo_selection = st.selectbox("Select a repository", repos)
            readme_content = fetch_readme(repo_selection)
            
            if readme_content:
                choice = st.radio("Chat with", ["README.md", "Files in Repo"])
                if choice == "README.md":
                    chat_with_content(readme_content)
                elif choice == "Files in Repo":
                    files = fetch_repo_files(repo_selection)
                    if files:
                        file_selection = st.selectbox("Select a file", files)
                        file_content = fetch_file_content(repo_selection, file_selection)
                        if file_content:
                            chat_with_content(file_content)
                        else:
                            st.error("Failed to fetch file content.")
                    else:
                        st.warning("No files found in repository.")
            else:
                st.warning("No README.md found for the selected repository.")
        else:
            st.warning(f"No repositories found for {github_username}.")
    else:
        st.warning("GitHub username cannot be empty.")

if __name__ == "__main__":
    main()
