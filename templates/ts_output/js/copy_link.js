"use strict";
function copyLink(passedUrl) {
    console.log(window.location);
    const currentLocation = window.location.toString();
    const locationRoot = currentLocation.split('/', 3).join("//");
    console.log(locationRoot);
    //navigator.clipboard.writeText(window.location.href); - requires HTTPS or localhost
    const url = document.createElement('input');
    if (passedUrl) {
        console.log('goti');
        url.setAttribute('value', locationRoot + passedUrl);
    }
    else {
        url.setAttribute('value', currentLocation);
    }
    document.body.appendChild(url);
    url.select();
    document.execCommand('copy');
    document.body.removeChild(url);
}
