import { expose } from "@/templates/ts/utils.ts"
import {
    comparePasswords,
    emailInput,
    getPasswordFeedback,
    inputFeedback,
    newObserver,
    passwordFeedbackOne,
    passwordFeedbackTwo,
    passwordInputOne,
    passwordInputTwo,
    processEmailValue,
    toggleSubmitButton,
    validateInputFeedback
} from "@/templates/userauth/account/ts/auth_helper.ts"

// triggered from x-init on the form
function setupObserversSignup() {

    if (inputFeedback == null) return
    newObserver(emailInput, inputFeedback, () => {
    })


    if (passwordFeedbackOne == null) return
    newObserver(passwordInputOne, passwordFeedbackOne, () => {
    })


    if (passwordFeedbackTwo == null) return
    newObserver(passwordInputTwo, passwordFeedbackTwo, () => {
    })
    evaluateButtonSignup()
}


function evaluateButtonSignup() {

    if (inputFeedback === null || passwordFeedbackOne === null || passwordFeedbackTwo === null) return
    toggleSubmitButton(true)
    /*    if (inputFeedback.innerText === '' || passwordFeedbackOne.innerText === '' || passwordFeedbackTwo.innerText === '') {
            toggleSubmitButton(true)
        } else {
            toggleSubmitButton(false)
        }*/


}


function validateSignup() {

    if (emailInput == null || passwordInputOne == null || passwordInputTwo == null || inputFeedback === null || passwordFeedbackOne === null || passwordFeedbackTwo === null) return

    let errorCount = 0
    errorCount += validateInputFeedback(emailInput, inputFeedback)
    errorCount += validateInputFeedback(passwordInputOne, passwordFeedbackOne)
    errorCount += validateInputFeedback(passwordInputTwo, passwordFeedbackTwo)

    return errorCount == 0

}

expose({
    comparePasswords,
    evaluateButtonSignup,
    getPasswordFeedback,
    processEmailValue,
    setupObserversSignup,
    validateSignup,
})
