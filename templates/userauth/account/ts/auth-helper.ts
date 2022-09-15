const emailInput = (<HTMLInputElement>document.getElementById('email-input'))
const inputFeedback: HTMLElement | null = document.getElementById('email-feedback')


const passwordFeedbackOne: HTMLElement | null = document.getElementById("password-feedback1")
const passwordFeedbackTwo: HTMLElement | null = document.getElementById("password-feedback2")

const passwordInputOne = (<HTMLInputElement>document.getElementById("password-input1"))
const passwordInputTwo = (<HTMLInputElement>document.getElementById("password-input2"))


const submitButton: HTMLButtonElement = <HTMLButtonElement>document.getElementById("submit-button")


//var targetEmail = document.getElementById('email-feedback')

//TODO: Have 3 observers and they trigger a method that collates results from the 3 existing ones, then unlock the button and skip checkFeedbackBeforeSubmit dodgy method
var observerEmail = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
        if (mutation.type === 'childList') {
            if (inputFeedback.innerText === '') {
                console.log('empty')
                console.log(inputFeedback.classList.contains('hidden'))
                if (!inputFeedback.classList.contains('hidden')) {

                    inputFeedback.classList.add('hidden')
                }
                console.log('LOOOL')
            } else {
                if (inputFeedback.classList.contains('hidden')) {
                    inputFeedback.classList.remove('hidden')
                }
            }
            console.log(inputFeedback.innerText)
        }
        console.log(mutation.type);
    });
});
var config = {childList: true};
observerEmail.observe(inputFeedback, config);


function processEmailValue() {
    //let inputFeedback: HTMLElement | null = document.getElementById('email-feedback')


    if (emailInput == null || inputFeedback == null) return
    const emailPassed = emailInput.value

    inputFeedback.classList.remove('hidden')
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


function validateEmail(address: string) {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,6})+$/.test(address)) {
        return true
    }
    return false
}


function toggleSubmitButton(toEnable: boolean) {
    //let submitButton: HTMLButtonElement = <HTMLButtonElement>document.getElementById("submit-button")

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

function comparePasswords() {
    //let passwordInputOne = (<HTMLInputElement>document.getElementById("password-input1"))
    //let passwordInputTwo = (<HTMLInputElement>document.getElementById("password-input2"))


    if (passwordInputOne == null || passwordInputTwo == null) return

    const passwordOne: string = passwordInputOne.value
    const passwordTwo: string = passwordInputTwo.value
    toggleSubmitButton(false)

    // check if one of the passwords is not empty
    if (passwordOne.length !== 0 && passwordTwo.length !== 0) {


        let passwordFeedbackOne: HTMLElement | null = document.getElementById("password-feedback1")
        let passwordFeedbackTwo: HTMLElement | null = document.getElementById("password-feedback2")

        if (passwordFeedbackOne != null && passwordFeedbackTwo != null) {
            passwordFeedbackTwo.classList.remove('hidden')

            // WARNING - includes is case-sensitive so make sure to match output of checkPasswordQuality()
            if (!passwordFeedbackOne.classList.contains("hidden")) {
                passwordFeedbackTwo.innerText = "Please enter a secure password above first."

            }

            // compare email input values
            else if (passwordOne !== passwordTwo) {
                passwordFeedbackTwo.innerText = "Sorry, passwords do not match."
            } else {
                //passwordFeedbackTwo.innerText = "Thank you, passwords do match."
                //toggleSubmitButton(true)
                if (!passwordFeedbackTwo.classList.contains('hidden')) {
                    passwordFeedbackTwo.classList.add('hidden')
                    toggleSubmitButton(true)
                }

            }
        }
    }
}

function getPasswordFeedback() {


    //let passwordFeedbackOne: HTMLElement | null = document.getElementById("password-feedback1")
    //let passwordFeedbackTwo: HTMLElement | null = document.getElementById("password-feedback2")

    if (passwordFeedbackOne != null && passwordFeedbackTwo != null) {

        //TODO: Should be really dependent on whether you are in login or sign up
        //toggleSubmitButton(false)

        //passwordFeedbackOne.classList.remove('hidden')


        const passwordEntered: string = (<HTMLInputElement>document.getElementById("password-input1")).value


        if (passwordEntered.length < 1)
            return


        const passwordQuality = checkPasswordQuality(passwordEntered)


        if (passwordQuality.includes("Secure") || passwordQuality.includes("Good")) {
            if (!passwordFeedbackOne.classList.contains('hidden')) {
                passwordFeedbackOne.classList.add('hidden')
                toggleSubmitButton(true)
            }
        } else {
            if (passwordFeedbackOne.classList.contains('hidden')) {
                passwordFeedbackOne.classList.remove('hidden')
            }

            passwordFeedbackOne.innerText = `Please improve your password!`

        }

    }
}


function checkPasswordQuality(pass: string) {

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
function scorePassword(pass: string) {
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

function checkFeedbackBeforeSubmit() {
    console.log(`hello ${event}`)
    if (!event) return
    if (submitButton == null || inputFeedback == null || passwordFeedbackOne == null || passwordFeedbackTwo == null) {
        event.preventDefault()
        return false
    }
    console.log('ok?')

    if (inputFeedback.classList.contains('hidden') && passwordFeedbackOne.classList.contains('hidden') && passwordFeedbackTwo.classList.contains('hidden')) {
        return true
    } else {
        event.preventDefault()
        toggleSubmitButton(false)
        return false
    }
    console.log('yay?')

}
