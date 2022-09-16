/* Needs auth-helper to run */

const emailInput = (<HTMLInputElement>document.getElementById('email-input'))
const inputFeedback: HTMLElement | null = document.getElementById('email-feedback')

const passwordInputOne = (<HTMLInputElement>document.getElementById("password-input1"))
const passwordFeedbackOne: HTMLElement | null = document.getElementById("password-feedback1")

const passwordInputTwo = (<HTMLInputElement>document.getElementById("password-input2"))
const passwordFeedbackTwo: HTMLElement | null = document.getElementById("password-feedback2")



const submitButton: HTMLButtonElement = <HTMLButtonElement>document.getElementById("submit-button")


// triggered from x-init on the form
function setupObservers() {

    if (inputFeedback == null) return
    newObserver(emailInput, inputFeedback)


    if (passwordFeedbackOne == null) return
    newObserver(passwordInputOne, passwordFeedbackOne)


    if (passwordFeedbackTwo == null) return
    newObserver(passwordInputTwo, passwordFeedbackTwo)

}



function evaluateButton() {

    if (inputFeedback === null || passwordFeedbackOne === null || passwordFeedbackTwo === null) return
    if (inputFeedback.innerText === '' && passwordFeedbackOne.innerText === '' && passwordFeedbackTwo.innerText === '') {
        toggleSubmitButton(true)
    } else {
        toggleSubmitButton(false)
    }


}

