addEventListener("DOMContentLoaded", (event) => {
    console.log("testttt")
});


let paused = true;
let captionStream = null;
let textTimingOffset = -0.5; // shift captions back a certain amount

browser.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        if (request.message === "start")
        {
            let zoomVideoElement = document.getElementById("vjs_video_3_html5_api") 
            zoomVideoElement.disablePictureInPicture = "true"; // Disable picture in picture
            zoomVideoElement.pause();

            zoomVideoElement.addEventListener("pause", () => {  // Pause or unpause youtube video if zoom video is paused or unpaused
                console.log("Video Paused");
                brainrotPlayer.contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*');
                paused = true;
            });
            zoomVideoElement.addEventListener("play", () => {
                console.log("Video Unpaused");
                brainrotPlayer.contentWindow.postMessage('{"event":"command","func":"playVideo","args":""}', '*');
                paused = false;
            });

            let videoplayer = document.getElementById("vjs_video_3_html5_api").parentElement.parentElement; // Get video player div so we can change its size
            
            videoHeight = videoplayer.style.height.replaceAll("px", "");
            videoWidth = videoplayer.style.width.replaceAll("px", "");
            reversedAspectRatio = videoHeight / videoWidth; // Get reversed aspect ratio so we can turn the video vertical
            console.log(Math.floor(videoHeight * reversedAspectRatio))

            brainrotWidth = Math.floor(videoHeight * reversedAspectRatio);
            videoplayer.style.width = brainrotWidth + "px";

            let videoPlayerOverlayElement = document.createElement("div") // New overlay to put youtube video in
            videoPlayerOverlayElement.classList.add("vjs-rec-overlay");
            zoomVideoElement.parentElement.insertBefore(videoPlayerOverlayElement, videoplayer.getElementsByClassName("vjs-rec-overlay")[0]);
            let brainrotPlayer = document.createElement("iframe");

            brainrotPlayer.id = "brainrotVideo";
            brainrotPlayer.classList.add("brainrotVideoPlayer")
            brainrotPlayer.width = brainrotWidth;
            brainrotPlayer.height = videoHeight;
            brainrotPlayer.src = "https://www.youtube.com/embed/s600FYgI5-s?si=3EjPEFVTB8281viQ&amp;showinfo=0&amp;autohide=1&amp;mute=1&amp;loop=1&amp;playlist=s600FYgI5-s&amp;controls=0&amp;rel=0&amp;enablejsapi=1";
            brainrotPlayer.title = "Brainrot Video";
            brainrotPlayer.allow = "autoplay;"
            brainrotPlayer.referrerPolicy = "strict-origin-when-cross-origin"
            brainrotPlayer.style = "position: relative; pointer-events: none;";
            brainrotPlayer.style.borderRadius = "7pt"

            videoPlayerOverlayElement.appendChild(brainrotPlayer); // Add youtube video

            let pauseElement = document.getElementById("vjs_video_3"); // Used to detect when the zoom video is paused

            console.log("Starting...")

            if(request.useStoredAlignedText)
            {
                console.log("Getting Stored Aligned Text...");
                fetch("http://127.0.0.1:6814/getStoredCaptionStream", {signal: AbortSignal.timeout(300000)}) // 3 minute timeout
                    .then((response) => {
                        return response.json();
                    })
                    .then((returnjson) => {
                        captionStream = returnjson.captionStream;
                        console.log(captionStream);
                    })
            }
            else
            {
                console.log("Aligning text (will take a while)...")
                fetch("http://127.0.0.1:6814/brainrot", {signal: AbortSignal.timeout(300000)}) // 3 minute timeout
                    .then((response) => {
                        return response.json();
                    })
                    .then((returnjson) => {
                        captionStream = returnjson.captionStream;
                        console.log(captionStream);
                    })
            }
            
            let textOverlay = document.createElement("div") // Overlay for our caption text to live in
            textOverlay.classList.add("vjs-rec-overlay");
            zoomVideoElement.parentElement.insertBefore(textOverlay, videoplayer.getElementsByClassName("vjs-rec-overlay")[1]);
            textOverlay.style = "display: flex; justify-content: center;"

            let caption = document.createElement("p");
            caption.style = "margin: auto; padding: 10pt; text-align: center; font-size: x-large; font-family: Roboto; Arial, Helvetica, sans-serif; font-weight: 600; text-shadow: -2px 0 black, 0 2px black, 2px 0 black, 0 -2px black;"
            textOverlay.appendChild(caption);

            // Import roboto font
            let fontsapi = document.createElement("link"); // google fonts api
            fontsapi.rel = "preconnect";
            fontsapi.href = "https://fonts.googleapis.com";
            document.head.appendChild(fontsapi);

            let gstaticimport = document.createElement("link") // gstatic thing idk
            gstaticimport.rel = "preconnect";
            gstaticimport.href = "https://fonts.gstatic.com";
            gstaticimport.crossOrigin = "anonymous";
            document.head.appendChild(gstaticimport);

            let robotoFont = document.createElement("link"); // actual font
            robotoFont.href = "https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap";
            robotoFont.rel = "stylesheet";
            document.head.appendChild(robotoFont);
            
            startBrainrot(zoomVideoElement, caption)
        }
    }
);

let currentCaptionIndex = 0 // minimize need to binary search for caption

function startBrainrot(zoomVideoElement, caption)
{
    setInterval(() => {
        if(!paused)
        {
            let currentTime = zoomVideoElement.currentTime - textTimingOffset;

            if(captionStream != null)
            {
                if(currentCaptionIndex == -1)
                {
                    caption.innerHTML = "";
                    currentCaptionIndex = searchForCaptionTime(currentTime, 0, captionStream.length)
                }
                else
                {
                    let currentCaption = captionStream[currentCaptionIndex];
                    let nextCaption = captionStream[currentCaptionIndex + 1];
                    if(isTimeInBetween(currentTime, currentCaption.minTime, currentCaption.maxTime))
                    {
                        caption.innerHTML = currentCaption.text;
                    }
                    else if (isTimeInBetween(currentCaption, nextCaption.minTime, nextCaption.maxTime)) // Check if we've entered the next caption
                    {
                        currentCaptionIndex++;
                    }
                    else // We're not in the next caption (likely because we've seeked ahead in the video) so just search for the current caption
                    {
                        currentCaptionIndex = searchForCaptionTime(currentTime, 0, captionStream.length)
                    }
                }
            }
        }
    }, 33);
}

function searchForCaptionTime(time, startIndex, endIndex)
{
    if(startIndex > endIndex) { return -1; }

    let middleIndex = Math.floor((startIndex + endIndex) / 2)
    let middle = captionStream[middleIndex];

    if(isTimeInBetween(time, middle.minTime, middle.maxTime)) { return middleIndex; }

    if(middle.minTime > time) { return searchForCaptionTime(time, startIndex,      middleIndex - 1); }
    else                      { return searchForCaptionTime(time, middleIndex + 1, endIndex       ); }
}

function isTimeInBetween(time, min, max)
{
    return time >= min && time < max;
}