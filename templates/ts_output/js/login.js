"use strict";
/* Needs auth-helper to run */
// triggered from x-init on the form
function setupObserversLogin() {
    if (inputFeedback == null)
        return;
    console.log('WTF2');
    newObserver(emailInput, inputFeedback, evaluateButtonLogin);
    //myfunction(this.evaluateButtonLogin)
}
function evaluateButtonLogin() {
    if (inputFeedback === null)
        return;
    if (inputFeedback.innerText === '') {
        toggleSubmitButton(true);
    }
    else {
        toggleSubmitButton(false);
    }
}
