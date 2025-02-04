addEventListener("DOMContentLoaded", (event) => {
    console.log("testttt")
});


browser.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.message === "start")
        {
            let videoplayer = document.getElementById("vjs_video_3_html5_api").parentElement.parentElement;

            videoHeight = videoplayer.style.height.replaceAll("px", "");
            videoWidth = videoplayer.style.width.replaceAll("px", "");
            reversedAspectRatio = videoHeight / videoWidth; 
            console.log(Math.floor(videoHeight * reversedAspectRatio))
            videoplayer.style.width = Math.floor(videoHeight * reversedAspectRatio) + "px";

            videoplayer.appendChild("")

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