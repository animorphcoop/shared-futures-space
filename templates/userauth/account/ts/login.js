/* Needs auth-helper to run */
var emailInput = document.getElementById('email-input');
var inputFeedback = document.getElementById('email-feedback');
var submitButton = document.getElementById("submit-button");
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
