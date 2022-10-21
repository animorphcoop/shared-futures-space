/* Needs auth-helper to run */

// triggered from x-init on the form
function setupObserversPsChange() {

    if (passwordFeedbackOne == null) return
    newObserver(passwordInputOne, passwordFeedbackOne, evaluateButtonPsChange)


    if (passwordFeedbackTwo == null) return
    newObserver(passwordInputTwo, passwordFeedbackTwo, evaluateButtonPsChange)

}


function evaluateButtonPsChange() {

    if (passwordFeedbackOne === null || passwordFeedbackTwo === null) return
    if (passwordFeedbackOne.innerText === '' || passwordFeedbackTwo.innerText === '') {
        toggleSubmitButton(true)
    } else {
        toggleSubmitButton(false)
    }


}


