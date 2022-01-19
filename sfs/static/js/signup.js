/*only if the email input field is 5+ chars we send request to django to check if it's valid.*/
function emailLength(input) {
    return input.length >= 5

}

function nameLength() {
    if (document.getElementById("display-input").value.length < 2) {
        const nameFeedback = document.getElementById("name-feedback")
        nameFeedback.innerText = "Please enter a name at least 2 characters long."
        nameFeedback.classList.value = 'text-incorrect'
        return false
    } else {
        return true
    }

}

//CHECK EMAILS
function compareEmails() {
    setTimeout(() => {
        const emailFeedback = document.getElementById("email-feedback")
        const emailFeedback2 = document.getElementById("email-feedback2")
        const correctClass = 'text-correct'
        const incorrectClass = 'text-incorrect'

        const emailOne = document.getElementById("email-input").value
        const emailTwo = document.getElementById("email-input2").value


        if (emailOne.length !== 0 && emailTwo.length !== 0) {

            // check if the first email is correct
            if (/^text-incorrect$/.test(emailFeedback.classList)) {
                emailFeedback2.innerText = "Please enter a correct email above first."
                emailFeedback2.classList.value = incorrectClass
            }
            // compare email input values
            else if (emailOne !== emailTwo) {
                emailFeedback2.classList.value = incorrectClass
                document.getElementById("email-feedback2").innerText = "Sorry, e-mails do not match."

            } else {
                emailFeedback2.classList.value = correctClass
                document.getElementById("email-feedback2").innerText = "Thank you for entering matching emails."
            }
        }
    }, 750)

}

// CHECK PASSWORDS
function comparePasswords() {
    setTimeout(() => {
        const passwordFeedback = document.getElementById("password-feedback1")
        const passwordFeedback2 = document.getElementById("password-feedback2")
        const correctClass = 'text-correct'
        const incorrectClass = 'text-incorrect'

        const passwordOne = document.getElementById("password-input1").value
        const passwordTwo = document.getElementById("password-input2").value

        // check if one of the passwords is not empty
        if (passwordOne.length !== 0 && passwordTwo.length !== 0) {

            // check if the first email is correct
            if (/^text-incorrect$/.test(passwordFeedback.classList)) {
                passwordFeedback2.classList.value = incorrectClass

                passwordFeedback2.innerText = "Please enter a secure password above first."
            }
            // compare email input values
            else if (passwordOne !== passwordTwo) {
                passwordFeedback2.classList.value = incorrectClass
                passwordFeedback2.innerText = "Sorry, passwords do not match."
                //signUpButton.disabled = true
                //signUpButton.classList.add('cursor-not-allowed')
            } else {
                passwordFeedback2.classList.value = correctClass
                passwordFeedback2.innerText = "Thank you, passwords do match."
                //signUpButton.disabled = false
                //signUpButton.classList.remove('cursor-not-allowed')
            }
        }
        evaluateButton()
    }, 500)
}

function passwordFeedback() {

    let passwordFeedback = document.getElementById("password-feedback1")
    const passwordEntered = document.getElementById("password-input1").value

    if (passwordEntered.length < 1)
        return


    const passwordQuality = checkPasswordQuality(passwordEntered)
    const correctClass = 'text-correct'
    const incorrectClass = 'text-incorrect'

    if (passwordQuality.includes("Secure")) {
        passwordFeedback.innerText = `${passwordQuality} password, well done!`
        passwordFeedback.classList.value = correctClass
    } else if (passwordQuality.includes("Good")) {
        passwordFeedback.innerText = `${passwordQuality} password, thank you.`
        passwordFeedback.classList.value = correctClass

    } else if (passwordQuality.includes("Weak")) {
        passwordFeedback.innerText = `${passwordQuality} password, spicy it up please!`
        passwordFeedback.classList.value = incorrectClass

    } else {
        passwordFeedback.innerText = `${passwordQuality} password, improve it please!`
        passwordFeedback.classList.value = incorrectClass

    }

    comparePasswords()

}

function checkPasswordQuality(pass) {

    console.log(pass)
    const score = scorePassword(pass);
    console.log(score)

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
function scorePassword(pass) {
    let score = 0;

    // variation range
    score += new Set(pass.split("")).size * 1;

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

    return parseInt(score);
}

function evaluateButton(){
    let feedbacks = []
    feedbacks.push(
        document.getElementById("email-feedback").classList,
        document.getElementById("email-feedback2").classList,
        document.getElementById("name-feedback").classList,
        document.getElementById("password-feedback1").classList,
        document.getElementById("password-feedback2").classList,
        )

    const incorrectFields = feedbacks.filter(checkIfCorrect)
    if (incorrectFields.length === 0){
        const signUpButton = document.getElementById("signup-button")
        signUpButton.disabled = false
        signUpButton.classList.remove('cursor-not-allowed')
    }


}

function checkIfCorrect(value, index, array) {
    return /^text-incorrect$/.test(value)
}