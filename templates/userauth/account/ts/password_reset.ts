/* Needs auth-helper to run - same as login - will be merged when TS files speak to each other*/
// TODO: merge with login? (now that the ts files do speak to each other)


import { expose } from "@/templates/ts/utils.ts"
import {
    emailInput,
    inputFeedback,
    newObserver,
    toggleSubmitButton,
    validateInputFeedback
} from "@/templates/userauth/account/ts/auth_helper.ts"

// triggered from x-init on the form
function setupObserversReset() {

    if (inputFeedback == null) return
    newObserver(emailInput, inputFeedback, ()=>{})
    toggleSubmitButton(true)

}



function validateReset() {

    if (inputFeedback === null) return
    let errorCount = 0
    errorCount += validateInputFeedback(emailInput, inputFeedback)
    return errorCount == 0

}

expose({
    setupObserversReset,
    validateReset,
})
