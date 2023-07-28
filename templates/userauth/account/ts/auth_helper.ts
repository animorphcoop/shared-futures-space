/* helper functions used in signup and login - import first!*/

export const emailInput = (<HTMLInputElement>document.getElementById("email-input"))
export const inputFeedback: HTMLElement | null = document.getElementById("email-feedback")

export const passwordInputOne = (<HTMLInputElement>document.getElementById("password-input1"))
export const passwordFeedbackOne: HTMLElement | null = document.getElementById("password-feedback1")

export const passwordInputTwo = (<HTMLInputElement>document.getElementById("password-input2"))
export const passwordFeedbackTwo: HTMLElement | null = document.getElementById("password-feedback2")


export const submitButton: HTMLButtonElement = <HTMLButtonElement>document.getElementById("submit-button")

export function newObserver(input: HTMLInputElement, feedback: HTMLElement, action: () => void) {
    const observerEmail = new MutationObserver(function (mutations) {
        mutations.forEach(function () {
            if (feedback.innerText === '') {
                if (!feedback.classList.contains('hidden')) {
                    feedback.classList.add('hidden')
                    input.setAttribute('borken', 'false')
                }
                action();

            } else {
                if (feedback.classList.contains('hidden')) {
                    feedback.classList.remove('hidden')
                    input.setAttribute('borken', 'true')
                }

            }

        })
    })
    let configEmail = {childList: true};
    observerEmail.observe(feedback, configEmail);
}


export function processEmailValue() {

    if (emailInput == null || inputFeedback == null) return
    const emailPassed = emailInput.value
    if (emailPassed.length <= 5) {
        inputFeedback.innerText = 'Please enter a valid email address.'
        return false
    } else {
        const returnValue = validateEmail(emailPassed)

        if (!returnValue) {
            inputFeedback.innerText = 'Please enter a valid email address.'
            return false
        } else {
            inputFeedback.innerText = ''
            return true
        }
    }

}


export function toggleSubmitButton(toEnable: boolean) {

    if (submitButton == null) return

    if (toEnable) {
        if (submitButton.classList.contains('cursor-not-allowed')) {
            submitButton.classList.remove('cursor-not-allowed')
            submitButton.disabled = false
        }
    } else {
        if (!submitButton.classList.contains('cursor-not-allowed')) {
            submitButton.classList.add('cursor-not-allowed')
            submitButton.disabled = true
        }
    }
}


export function validateEmail(address: string) {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,6})+$/.test(address)) {
        return true
    }
    return false
}


export function validateInputFeedback(input: HTMLInputElement, feedback: HTMLElement,) {
    if (input.value.length < 1 || feedback.innerText != '') {
        input.setAttribute("borken", "true");
        return 1
    } else {
        return 0
    }
}

export function comparePasswords() {
    if (passwordInputOne == null || passwordInputTwo == null) return

    const passwordOne: string = passwordInputOne.value
    const passwordTwo: string = passwordInputTwo.value

    // check if one of the passwords is not empty
    if (passwordOne.length !== 0 && passwordTwo.length !== 0) {

        if (passwordFeedbackOne != null && passwordFeedbackTwo != null) {
            if (passwordFeedbackOne.innerText !== '') {
                passwordFeedbackTwo.innerText = 'Please enter a secure password above first.'

            } else if (passwordOne !== passwordTwo) {
                passwordFeedbackTwo.innerText = 'Sorry, passwords do not match.'
            } else {
                passwordFeedbackTwo.innerText = ''
            }
        }
    }

}

export function getPasswordFeedback() {
    if (passwordFeedbackOne != null && passwordFeedbackTwo != null) {

        const passwordEntered: string = (<HTMLInputElement>document.getElementById("password-input1")).value

        if (passwordEntered.length < 1)
            return


        const passwordQuality = checkPasswordQuality(passwordEntered)


        if (passwordQuality.includes("Secure") || passwordQuality.includes("Good")) {
            passwordFeedbackOne.innerText = ''

        } else {
            passwordFeedbackOne.innerText = 'Strengthen your password; at least 10 characters using a mix of lowercase, uppercase, numbers, and special characters.'
        }
        comparePasswords()

    }
}


export function checkPasswordQuality(pass: string) {

    const score = scorePassword(pass);

    if (score > 80)
        return "Secure"
    else if (score > 60)
        return "Good"
    else if (score >= 30)
        return "Weak"
    else
        return "Tragic"
}


/*
* Used
* https://stackoverflow.com/questions/948172/password-strength-meter#comment120524342_11268104
* */
export function scorePassword(pass: string) {
    let score = 0;

    // variation range
    score += new Set(pass.split("")).size;

    // shuffle score - bonus for messing things up. 0 score for playing with upper/lowercase.
    const charCodes = pass.split('').map(x => x.toLowerCase().charCodeAt(0));
    for (let i = 1; i < charCodes.length; i++) {
        const dist = Math.abs(charCodes[i - 1] - charCodes[i]);
        if (dist > 60)
            score += 15;
        else if (dist > 1)
            score += 5;
    }

    // bonus for length
    score += (pass.length - 6) * 3;

    return parseInt(String(score));
}

