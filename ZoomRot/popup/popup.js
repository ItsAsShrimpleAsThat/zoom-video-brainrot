let goButton = document.getElementById("go");
let connectionStatus = document.getElementById("connectionStatus");
let useStoredAlignedText = document.getElementById("useStoredAlignedText");

function go(tabs)
{
    browser.tabs.sendMessage(tabs[0].id, {"message": "start", "useStoredAlignedText": useStoredAlignedText.checked });
}

goButton.disabled = true;
function contact(tabs)
{
    fetch("http://127.0.0.1:6814/contact")
        .then((response) => {
            if(!response.ok) 
            {
                goButton.disabled = true;
            }
            return response.json();
        })
        .then((returnjson) => {
            if(returnjson.status === "Contact.")
            {
                connectionStatus.innerHTML = "Connected";
                goButton.disabled = false;
            }
        })
        .catch((error) => {
            connectionStatus.innerHTML = "Unconnected";
            goButton.disabled = true;
        })
}

goButton.addEventListener("click", function(){
    browser.tabs
        .query({ active: true, currentWindow: true })
        .then(go)
});

// Search for Python processor
setInterval(() => {
    browser.tabs
        .query({ active: true, currentWindow: true })
        .then(contact)
}, 1000);
