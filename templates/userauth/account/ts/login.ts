/* Needs auth-helper to run */


// triggered from x-init on the form
function setupObserversLogin() {

    if (inputFeedback == null) return
    newObserver(emailInput, inputFeedback, evaluateButtonLogin())

}



function evaluateButtonLogin() {

    if (inputFeedback === null) return
    if (inputFeedback.innerText === '') {
        toggleSubmitButton(true)
    } else {
        toggleSubmitButton(false)
    }


}


