addEventListener("DOMContentLoaded", (event) => {
    let videoplayer = document.getElementsByClassName("transcript-wrapper")[0];

    videoplayer.style.width = "10px";

    console.log("testttt")
});


browser.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.message === "start")
        {
            console.log("Starting...")

            fetch("http://127.0.0.1:6814/alive")
                .then((response) => {
                    return response.json();
                })
                .then((returnjson) => {
                    console.log(returnjson.message)
                })
        }
    }
);