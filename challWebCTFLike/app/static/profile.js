function updateProfil(dict) {
    fetch('/profil', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dict)
    }).then(response => response.json())
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            console.error("can't reach server");
        });
}