var script = document.createElement('script');
script.src = 'https://code.jquery.com/jquery-3.6.3.min.js'; // Check https://jquery.com/ for the current version
document.getElementsByTagName('head')[0].appendChild(script);

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
            let brainrotPlayer = document.createElement("iframe");

            brainrotPlayer.id = "brainrotVideo";
            brainrotPlayer.classList.add("brainrotVideoPlayer")
            brainrotPlayer.width = brainrotWidth;
            brainrotPlayer.height = videoHeight;
            brainrotPlayer.src = "https://www.youtube.com/embed/s600FYgI5-s?si=3EjPEFVTB8281viQ&amp;showinfo=0&amp;autohide=1&amp;mute=1&amp;controls=0?rel=0&amp;autoplay=1&amp;enablejsapi=1";
            brainrotPlayer.title = "Brainrot Video";
            brainrotPlayer.allow = "autoplay;"
            brainrotPlayer.referrerPolicy = "strict-origin-when-cross-origin"
            brainrotPlayer.style = "position: relative; pointer-events: none;";
            brainrotPlayer.style.borderRadius = "7pt"

            videoPlayerOverlayElement.appendChild(brainrotPlayer);

            unselectable
            videoPlayerOverlayElement.appendChild()

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