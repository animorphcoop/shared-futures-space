"use strict";
const postcodeContainer = document.getElementById("postcode-change");
const postcodeChangeInput = document.getElementById("postcode");
function togglePostcodeChange() {
    if (postcodeContainer == null)
        return;
    postcodeContainer.classList.toggle('hidden');
}
function validatePostcode() {
    if (postcodeChangeInput == null)
        return;
    let errorCount = 0;
    if (postcodeChangeInput.value.length < 1) {
        postcodeChangeInput.setAttribute("required", "");
        errorCount++;
    }
    else {
        togglePostcodeChange();
    }
    return errorCount === 0;
}
