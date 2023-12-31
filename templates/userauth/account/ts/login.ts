/* Needs auth-helper to run */

import {newObserver, inputFeedback, processEmailValue, emailInput, toggleSubmitButton} from './auth_helper.ts'
import {expose} from "@/templates/ts/utils.ts";

expose({ setupObserversLogin, processEmailValue })

// triggered from x-init on the form
function setupObserversLogin() {

    if (inputFeedback == null) return
    newObserver(emailInput, inputFeedback, evaluateButtonLogin)

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


