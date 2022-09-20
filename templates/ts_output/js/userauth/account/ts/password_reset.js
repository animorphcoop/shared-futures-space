"use strict";
/* Needs auth-helper to run - same as login - will be merged when TS files speak to each other*/
const emailInput = document.getElementById('email-input');
const inputFeedback = document.getElementById('email-feedback');
const submitButton = document.getElementById("submit-button");
// triggered from x-init on the form
function setupObservers() {
    if (inputFeedback == null)
        return;
    newObserver(emailInput, inputFeedback);
}
function evaluateButton() {
    if (inputFeedback === null)
        return;
    if (inputFeedback.innerText === '') {
        toggleSubmitButton(true);
    }
    else {
        toggleSubmitButton(false);
    }
}
