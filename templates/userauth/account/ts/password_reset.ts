/* Needs auth-helper to run - same as login - will be merged when TS files speak to each other*/


// triggered from x-init on the form
function setupObserversReset() {

    if (inputFeedback == null) return
    newObserver(emailInput, inputFeedback, evaluateButtonReset())


}



function evaluateButtonReset() {

    if (inputFeedback === null) return
    if (inputFeedback.innerText === '') {
        toggleSubmitButton(true)
    } else {
        toggleSubmitButton(false)
    }


}


