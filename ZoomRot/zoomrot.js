addEventListener("DOMContentLoaded", (event) => {
    console.log("testttt")
});

browser.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.message === "start")
        {
            let zoomVideoElement = document.getElementById("vjs_video_3_html5_api") 
            zoomVideoElement.disablePictureInPicture = "true"; // Disable picture in picture
            zoomVideoElement.pause();

            let videoplayer = document.getElementById("vjs_video_3_html5_api").parentElement.parentElement; // Get video player div so we can change its size
            
            videoHeight = videoplayer.style.height.replaceAll("px", "");
            videoWidth = videoplayer.style.width.replaceAll("px", "");
            reversedAspectRatio = videoHeight / videoWidth; // Get reversed aspect ratio so we can turn the video vertical
            console.log(Math.floor(videoHeight * reversedAspectRatio))

            brainrotWidth = Math.floor(videoHeight * reversedAspectRatio);
            videoplayer.style.width = brainrotWidth + "px";

            let videoPlayerOverlayElement = videoplayer.getElementsByClassName("vjs-rec-overlay")[0] // Overlay to put youtube video in
            let brainrotPlayer = document.createElement("iframe");

            brainrotPlayer.id = "brainrotVideo";
            brainrotPlayer.classList.add("brainrotVideoPlayer")
            brainrotPlayer.width = brainrotWidth;
            brainrotPlayer.height = videoHeight;
            brainrotPlayer.src = "https://www.youtube.com/embed/s600FYgI5-s?si=3EjPEFVTB8281viQ&amp;showinfo=0&amp;autohide=1&amp;mute=1&amp;loop=1&amp;controls=0&amp;rel=0&amp;enablejsapi=1";
            brainrotPlayer.title = "Brainrot Video";
            brainrotPlayer.allow = "autoplay;"
            brainrotPlayer.referrerPolicy = "strict-origin-when-cross-origin"
            brainrotPlayer.style = "position: relative; pointer-events: none;";
            brainrotPlayer.style.borderRadius = "7pt"

            videoPlayerOverlayElement.appendChild(brainrotPlayer); // Add youtube video

            let pauseElement = document.getElementById("vjs_video_3"); // Used to detect when the zoom video is paused
            
            videoplayer.addEventListener("click", function() { pauseUnpauseBrainrot(brainrotPlayer, pauseElement); }); // Listener to automatically pause brainrot when the zoom video is paused

            console.log("Starting...")

            fetch("http://127.0.0.1:6814/getStoredCaptionStream", {signal: AbortSignal.timeout(300000)}) // 3 minute timeout
                .then((response) => {
                    return response.json();
                })
                .then((returnjson) => {
                    console.log(returnjson.captionStream)
                })
        }
    }
);

function pauseUnpauseBrainrot(brainrotPlayer, pauseElement)
{
    console.log(pauseElement.classList)
    if(pauseElement.classList.contains("vjs-playing"))
    {
        console.log("Video Paused");
        brainrotPlayer.contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*')
    }
    else if(pauseElement.classList.contains("vjs-paused"))
    {
        console.log("Video Unpaused");
        brainrotPlayer.contentWindow.postMessage('{"event":"command","func":"playVideo","args":""}', '*')
    }
}