"use strict";
function swapHearts(buttonText) {
    const heart = document.getElementById('heart-icon');
    if (heart == null)
        return;
    if (buttonText.includes("SAVED")) {
        console.log('ok');
        heart.classList.remove('hidden');
    }
    else {
        console.log('nook');
        heart.hidden = false;
    }
}
