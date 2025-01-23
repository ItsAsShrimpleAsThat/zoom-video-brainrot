console.log("testmogsnackduke")
console.log("I AM GOING TO FUCKING KILL MYSELF WHY ISNT THIS WORKING")
addEventListener("DOMContentLoaded", (event) => {
    let videoplayer = document.getElementsByClassName("transcript-wrapper")[0];

    videoplayer.style.width = "10px";

    console.log("testttt")
});

browser.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        console.log("WHAT THE FUCK")
    }
);