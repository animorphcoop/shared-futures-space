function copyLink(passedUrl: string) {
    const currentLocation = window.location.toString()
    const locationRoot = currentLocation.split('/', 3).join("//")
    //navigator.clipboard.writeText(window.location.href); - requires HTTPS or localhost
    const url = document.createElement('input');
    if (passedUrl) {
        url.setAttribute('value', locationRoot+passedUrl);

    } else {
        url.setAttribute('value', currentLocation);

    }
    document.body.appendChild(url);
    url.select();
    document.execCommand('copy');
    document.body.removeChild(url);
}