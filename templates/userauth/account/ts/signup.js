/* Needs auth-helper to run */
var emailInput = document.getElementById('email-input');
var inputFeedback = document.getElementById('email-feedback');
var passwordInputOne = document.getElementById("password-input1");
var passwordFeedbackOne = document.getElementById("password-feedback1");
var passwordInputTwo = document.getElementById("password-input2");
var passwordFeedbackTwo = document.getElementById("password-feedback2");
var submitButton = document.getElementById("submit-button");
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
