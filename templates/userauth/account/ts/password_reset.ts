import { expose } from "@/templates/ts/utils.ts"
import {
    emailInput,
    inputFeedback,
    newObserver,
    processEmailValue,
    toggleSubmitButton,
    validateInputFeedback,
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
    processEmailValue,
    setupObserversReset,
    validateReset,
})
