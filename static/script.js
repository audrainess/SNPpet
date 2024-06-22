document.getElementById('conversion-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    fetch('/convert', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const outputData = document.getElementById('output-data');
        outputData.innerHTML = `
            <p>${data.format1} <button onclick="copyToClipboard('${data.format1}')">Copy</button></p>
            <p>${data.format2} <button onclick="copyToClipboard('${data.format2}')">Copy</button></p>
            <p>${data.format3} <button onclick="copyToClipboard('${data.format3}')">Copy</button></p>
        `;
    })
    .catch(error => console.error('Error:', error));
});

document.getElementById('liftover-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    fetch('/liftover', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const liftoverOutput = document.getElementById('liftover-output');
        liftoverOutput.textContent = `Converted position: ${data.liftover_result}`;
    })
    .catch(error => console.error('Error:', error));
});

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('Copied to clipboard');
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}
