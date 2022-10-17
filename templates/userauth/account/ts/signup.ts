/* Needs auth-helper to run */
const signupForm: HTMLFormElement = (<HTMLFormElement>document.getElementById("signup_form"))


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
    if (inputFeedback.innerText === '' || passwordFeedbackOne.innerText === '' || passwordFeedbackTwo.innerText === '') {
        toggleSubmitButton(true)
    } else {
        toggleSubmitButton(false)
    }


}


function validateSignup() {
    if (emailInput == null || passwordInputOne == null || passwordInputTwo == null || inputFeedback === null || passwordFeedbackOne === null || passwordFeedbackTwo === null) return

    let errorCount = 0
    errorCount += validateInputFeedback(emailInput, inputFeedback)
    errorCount += validateInputFeedback(passwordInputOne, passwordFeedbackOne)
    errorCount += validateInputFeedback(passwordInputTwo, passwordFeedbackTwo)

    return errorCount == 0



}
