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

            brainrotWidth = Math.floor(videoHeight * reversedAspectRatio);
            videoplayer.style.width = brainrotWidth + "px";

            let videoPlayerOverlayElement = videoplayer.getElementsByClassName("vjs-rec-overlay")[0]
            let rot = document.createElement("iframe");

            rot.id = "brainrotVideo";
            rot.width = brainrotWidth;
            rot.height = videoHeight;
            rot.src = "https://www.youtube.com/embed/s600FYgI5-s?si=3EjPEFVTB8281viQ&amp;mute=1&amp;controls=0?rel=0&amp;autoplay=1";
            rot.title = "Brainrot Video";
            rot.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; web-share"
            rot.referrerPolicy = "strict-origin-when-cross-origin"
            rot.style = "position: relative; ";
            videoPlayerOverlayElement.appendChild(rot);

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