"use strict";
/* Needs auth-helper to run */
const emailInput = document.getElementById('email-input');
const inputFeedback = document.getElementById('email-feedback');
const passwordInputOne = document.getElementById("password-input1");
const passwordFeedbackOne = document.getElementById("password-feedback1");
const passwordInputTwo = document.getElementById("password-input2");
const passwordFeedbackTwo = document.getElementById("password-feedback2");
const submitButton = document.getElementById("submit-button");
// triggered from x-init on the form
function setupObservers() {
    if (inputFeedback == null)
        return;
    newObserver(emailInput, inputFeedback);
    if (passwordFeedbackOne == null)
        return;
    newObserver(passwordInputOne, passwordFeedbackOne);
    if (passwordFeedbackTwo == null)
        return;
    newObserver(passwordInputTwo, passwordFeedbackTwo);
}
function evaluateButton() {
    if (inputFeedback === null || passwordFeedbackOne === null || passwordFeedbackTwo === null)
        return;
    if (inputFeedback.innerText === '' && passwordFeedbackOne.innerText === '' && passwordFeedbackTwo.innerText === '') {
        toggleSubmitButton(true);
    }
    else {
        toggleSubmitButton(false);
    }
}
