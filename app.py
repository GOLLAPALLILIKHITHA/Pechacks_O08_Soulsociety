from flask import Flask, request, jsonify, send_file, render_template
import requests
import base64
import google.generativeai as genai
from fpdf import FPDF
import os

# API keys
GITHUB_API_TOKEN = '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'
GEMINI_API_KEY = 'AIzaSyBBZ5_9tGyMUYBnLF3qbjUTB_Mfrd7bfm8'

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

# Helper Functions
def fetch_github_repos(username):
    url = f'https://api.github.com/users/{username}/repos'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repos = response.json()
        return [repo['full_name'] for repo in repos]
    return []

def fetch_readme(repo_full_name):
    url = f'https://api.github.com/repos/{repo_full_name}/contents/README.md'
    headers = {'Authorization': f'token {GITHUB_API_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return base64.b64decode(data['content']).decode('utf-8')
    return None

def generate_gemini_docs(readme_content):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(readme_content)
    return response.text if response and response.text else "Failed to generate documentation."

def save_pdf(content, pdf_filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, content)
    pdf.output(pdf_filename)
    return pdf_filename

# New function to generate conversation/chat with repo
def generate_chat_with_repo(repo_full_name, user_input):
    readme_content = fetch_readme(repo_full_name)
    if not readme_content:
        return "Failed to retrieve README content."
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.converse(readme_content, user_input)
    return response.text if response and response.text else "Failed to generate conversation."


# Routes
@app.route('/')
def home():
    return render_template('index.html') # Render the HTML file

@app.route('/fetch_repos', methods=['POST'])
def fetch_repos():
    data = request.json
    username = data.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    repos = fetch_github_repos(username)
    if repos:
        return jsonify({"repos": repos}), 200
    return jsonify({"error": "No repositories found"}), 404

@app.route('/generate_docs', methods=['POST'])
def generate_docs():
    data = request.json
    repo_full_name = data.get('repo_full_name')
    if not repo_full_name:
        return jsonify({"error": "Repository full name is required"}), 400
    
    readme_content = fetch_readme(repo_full_name)
    if not readme_content:
        return jsonify({"error": "README.md not found"}), 404
    
    documentation = generate_gemini_docs(readme_content)
    if not documentation:
        return jsonify({"error": "Failed to generate documentation"}), 500
    
    pdf_filename = f"{repo_full_name.replace('/', '_')}_documentation.pdf"
    save_pdf(documentation, pdf_filename)
    return jsonify({"documentation": documentation, "pdf_filename": pdf_filename}), 200

@app.route('/generate_chat', methods=['POST'])
def generate_chat():
    data = request.json
    repo_full_name = data.get('repo_full_name')
    user_input = data.get('user_input')
    
    if not repo_full_name or not user_input:
        return jsonify({"error": "Repository full name and user input are required"}), 400
    
    chat_response = generate_chat_with_repo(repo_full_name, user_input)
    if not chat_response:
        return jsonify({"error": "Failed to generate chat"}), 500
    
    return jsonify({"chat": chat_response}), 200


@app.route('/download_pdf/<filename>', methods=['GET'])
def download_pdf(filename):
    file_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
