document.getElementById('searchForm').onsubmit = async (event) => {
    event.preventDefault();
    const form = new FormData(event.target);
    const params = new URLSearchParams(form);
    const response = await fetch(`/papers?${params}`);
    const papers = await response.json();
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = papers
        .map((paper) => `<a href="/download/${paper.filename}">${paper.filename}</a><br>`)
        .join('');
};
document.querySelector("#uploadForm").onsubmit = async function (e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const response = await fetch('/admin', {
        method: 'POST',
        body: formData,
    });

    const messageDiv = document.getElementById('message');
    if (response.ok) {
        const successMessage = await response.text();
        messageDiv.innerHTML = `<p style="color:green;">${successMessage}</p>`;
        document.getElementById('uploadForm').reset();
    } else {
        const errorMessage = await response.text();
        messageDiv.innerHTML = `<p style="color:red;">${errorMessage}</p>`;
    }
};
