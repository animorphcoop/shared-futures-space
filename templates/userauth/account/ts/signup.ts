/* Needs auth-helper to run */


// triggered from x-init on the form
function setupObserversSignup() {

    if (inputFeedback == null) return
    newObserver(emailInput, inputFeedback, evaluateButtonSignup)


    if (passwordFeedbackOne == null) return
    newObserver(passwordInputOne, passwordFeedbackOne, evaluateButtonSignup)


    if (passwordFeedbackTwo == null) return
    newObserver(passwordInputTwo, passwordFeedbackTwo, evaluateButtonSignup)

}


function evaluateButtonSignup() {

    if (inputFeedback === null || passwordFeedbackOne === null || passwordFeedbackTwo === null) return
    if (inputFeedback.innerText === '' && passwordFeedbackOne.innerText === '' && passwordFeedbackTwo.innerText === '') {
        toggleSubmitButton(true)
    } else {
        toggleSubmitButton(false)
    }


}

