import { expose } from "@/templates/ts/utils.ts"
import {
    comparePasswords,
    getPasswordFeedback,
    newObserver,
    passwordFeedbackOne,
    passwordFeedbackTwo,
    passwordInputOne,
    passwordInputTwo,
    toggleSubmitButton, validateInputFeedback,
} from "@/templates/userauth/account/ts/auth_helper.ts"

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

function validateResetKey() {

    if (passwordFeedbackOne === null) return
    let errorCount = 0
    errorCount += validateInputFeedback(passwordInputOne, passwordFeedbackOne)
    return errorCount == 0

}

expose({
    comparePasswords,
    evaluateButtonPsChange,
    getPasswordFeedback,
    setupObserversPsChange,
    validateResetKey,
})
