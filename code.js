document.getElementById('submit-btn').addEventListener('click', () => {
    const githubLink = document.getElementById('github-link').value;
    if (!githubLink) {
        alert('Please enter a GitHub link!');
        return;
    }

    // Fetch repositories logic (placeholder)
    const repoList = document.getElementById('repo-list');
    repoList.innerHTML = ''; // Clear previous items
    const repos = ['Repo 1', 'Repo 2', 'Repo 3']; // Simulated repo names
    repos.forEach(repo => {
        const listItem = document.createElement('li');
        listItem.textContent = repo;
        listItem.onclick = () => showRepoDetails(repo);
        repoList.appendChild(listItem);
    });

    document.getElementById('repo-list-section').style.display = 'block';
});

function showRepoDetails(repo) {
    document.getElementById('repo-list-section').style.display = 'none';
    document.getElementById('repo-details-section').style.display = 'flex';

    // Display placeholder content
    document.getElementById('code-content').textContent = '// Code for ${repo}';
    document.getElementById('website-preview').textContent = 'Website preview for ${repo}';
}

document.getElementById('chat-btn').addEventListener('click', () => {
    const query = document.getElementById('chat-input').value;
    if (!query) {
        alert('Enter your question!');
        return;
    }

    // Simulate code generation and website preview
    document.getElementById('code-content').textContent = 'Generated code will appear here.';
    document.getElementById('website-preview').textContent = 'Live website preview will load here.';
});