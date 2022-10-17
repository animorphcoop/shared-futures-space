"use strict";
/* Needs auth-helper to run */
const signupForm = document.getElementById("signup_form");
// triggered from x-init on the form
function setupObserversSignup() {
    if (inputFeedback == null)
        return;
    newObserver(emailInput, inputFeedback, evaluateButtonSignup);
    if (passwordFeedbackOne == null)
        return;
    newObserver(passwordInputOne, passwordFeedbackOne, evaluateButtonSignup);
    if (passwordFeedbackTwo == null)
        return;
    newObserver(passwordInputTwo, passwordFeedbackTwo, evaluateButtonSignup);
}
function evaluateButtonSignup() {
    if (inputFeedback === null || passwordFeedbackOne === null || passwordFeedbackTwo === null)
        return;
    if (inputFeedback.innerText === '' || passwordFeedbackOne.innerText === '' || passwordFeedbackTwo.innerText === '') {
        console.log('about to enable');
        toggleSubmitButton(true);
    }
    else {
        console.log('about to disable');
        toggleSubmitButton(false);
    }
}
function validateSignup() {
    if (emailInput == null || passwordInputOne == null || passwordInputTwo == null)
        return;
    if (inputFeedback === null || passwordFeedbackOne === null || passwordFeedbackTwo === null)
        return;
    console.log(emailInput);
    let readyToGo = true;
    if (emailInput.value.length < 1 || inputFeedback.innerText != '') {
        //emailInput.setAttribute("required", "");
        emailInput.setAttribute("borken", "true");
        readyToGo = false;
    }
    if (passwordInputOne.value.length < 1 || passwordFeedbackOne.innerText != '') {
        passwordInputOne.setAttribute("borken", "true");
        readyToGo = false;
    }
    if (passwordInputTwo.value.length < 1 || passwordFeedbackTwo.innerText != '') {
        passwordInputTwo.setAttribute("borken", "true");
        readyToGo = false;
    }
    console.log('not going');
    if (readyToGo) {
        signupForm.submit();
    }
}
