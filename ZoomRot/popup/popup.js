function start(tabs)
{
    browser.tabs.sendMessage(tabs[0].id, {"message": "start"});
}

let goButton = document.getElementById("go");

goButton.addEventListener("click", function(){
    browser.tabs
        .query({ active: true, currentWindow: true })
        .then(start)
});
