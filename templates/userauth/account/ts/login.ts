/* Needs auth-helper to run */

// triggered from x-init on the form
function setupObserversLogin() {

    if (inputFeedback == null) return
    newObserver(emailInput, inputFeedback, evaluateButtonLogin)

    /*Setup observer on start check if fill automatically triggered*/
    //loginAutofillObserver(emailInput, listenForAutofill)


    /*
    * listen for value change and see autofill with a delay
    * it is because onfocusout event is not triggered with autofill
    * and hence processEmailValue() method does not run automatically
    * */
    emailInput.oninput = () => {
        processEmailValue()
        listenForAutofill()
    }

}

/*
 * detecting browser autofill on login page
 * https://developer.mozilla.org/en-US/docs/Web/CSS/:autofill
 * in case autofill is ridicilous we still want to filter
 * */
function listenForAutofill() {
    setTimeout(() => {
        if (emailInput.matches(':autofill')) {
            evaluateButtonLogin()
        }
    }, 250)
}

function evaluateButtonLogin() {

    if (inputFeedback === null) return
    if (inputFeedback.innerText === '') {
        toggleSubmitButton(true)
    } else {
        toggleSubmitButton(false)
    }


}


