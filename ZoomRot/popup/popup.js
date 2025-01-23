let goButton = document.getElementById("go");

function go(tabs)
{
    browser.tabs.sendMessage(tabs[0].id, {"message": "start"});
}

let test = document.getElementById("testtest");

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
            test.innerHTML = returnjson.status;
            if(returnjson.status === "Contact.")
            {
                goButton.disabled = false;
            }
        })
        .catch((error) => {
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
