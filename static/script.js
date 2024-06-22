document.getElementById('conversion-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    fetch('/convert', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        const outputData = document.getElementById('output-data');
        if (data.error) {
            outputData.innerHTML = `<p>Error: ${data.error}</p>`;
        } else {
            outputData.innerHTML = `
                <p>Franklin: ${data.franklin} <button onclick="copyToClipboard('${data.franklin}')">Copy</button></p>
                <p>UCSC Genome Browser: ${data.ucsc} <button onclick="copyToClipboard('${data.ucsc}')">Copy</button></p>
                <p>ClinVar: ${data.clinvar} <button onclick="copyToClipboard('${data.clinvar}')">Copy</button></p>
                <p>gnomAD: ${data.gnomad} <button onclick="copyToClipboard('${data.gnomad}')">Copy</button></p>
                <p>Other: ${data.other} <button onclick="copyToClipboard('${data.other}')">Copy</button></p>
            `;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('output-data').innerHTML = `<p>Error: ${error.message}</p>`;
    });
});

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('Copied to clipboard');
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}

document.getElementById('liftover-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    fetch('/liftover', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        const liftoverOutput = document.getElementById('liftover-output');
        if (data.error) {
            liftoverOutput.innerHTML = `<p>Error: ${data.error}</p>`;
        } else {
            liftoverOutput.innerHTML = `<p>Lifted coordinates: ${data.liftover_result}</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('liftover-output').innerHTML = `<p>Error: ${error.message}</p>`;
    });
});
