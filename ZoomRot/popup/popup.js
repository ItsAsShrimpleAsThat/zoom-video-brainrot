
let goButton = document.getElementById("go");

function pleasefuckingwork(tabs)
{
    browser.tabs.sendMessage(tabs[0].id, {"message": "hello?"});
}

goButton.addEventListener("click", function(){
    browser.tabs
        .query({ active: true, currentWindow: true })
        .then(pleasefuckingwork)
    
});
