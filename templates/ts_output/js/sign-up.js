"use strict";
/*
* Variables for the component
*/
/*

const correctClass: string = 'text-correct'
const incorrectClass: string = 'text-incorrect'
*/
/*
* Methods for the component
*/
/*
/!*only if the email input field is 5+ chars we send request to django to check if it's valid.*!/
function emailLength(textInput: string) {
    return textInput.length >= 5
}*/
/*
function nameLength(): boolean {
    const inputValue: string = (<HTMLInputElement>document.getElementById("display-input")).value;
    let result: boolean = false
    if (inputValue.length < 2) {
        const nameFeedback: HTMLElement | null = document.getElementById("name-feedback")
        if (nameFeedback != null) {
            nameFeedback.innerText = "Please enter a name at least 2 characters long."
            nameFeedback.classList.value = incorrectClass
        }
        result = false
    } else {
        result = true
    }
    setTimeout(() => {
        evaluateButton()
    }, 500)
    return result
}*/
/*

//CHECK EMAILS
function compareEmails() {
    setTimeout(() => {
        const emailFeedback: HTMLElement | null = document.getElementById("email-feedback")
        const emailFeedback2: HTMLElement | null = document.getElementById("email-feedback2")

        const emailOne = (<HTMLInputElement>document.getElementById("email-input")).value
        const emailTwo = (<HTMLInputElement>document.getElementById("email-input2")).value


        if (emailOne.length !== 0 && emailTwo.length !== 0) {

            if (emailFeedback != null && emailFeedback2 != null) {
                const emailFeedbackClasses: DOMTokenList = emailFeedback.classList
                let emailFeedbackClasses2: DOMTokenList = emailFeedback2.classList

                // check if the first email is correct
                if (/^text-incorrect$/.test(String(emailFeedbackClasses))) {
                    emailFeedback2.innerText = "Please enter a correct email above first."
                    emailFeedback2.classList.value = incorrectClass
                }
                // compare email input values
                else if (emailOne !== emailTwo) {
                    emailFeedback2.classList.value = incorrectClass
                    emailFeedback2.innerText = "Sorry, e-mails do not match."

                } else {
                    emailFeedbackClasses2.value = correctClass
                    emailFeedback2.innerText = "Thank you for entering matching emails."
                }
            }
        }
        evaluateButton()
    }, 750)
}

*/
// CHECK PASSWORDS
function comparePasswords() {
    setTimeout(() => {
        const passwordFeedback = document.getElementById("password-feedback1");
        const passwordFeedback2 = document.getElementById("password-feedback2");
        const passwordOne = document.getElementById("password-input1").value;
        const passwordTwo = document.getElementById("password-input2").value;
        // check if one of the passwords is not empty
        if (passwordOne.length !== 0 && passwordTwo.length !== 0) {
            if (passwordFeedback != null && passwordFeedback2 != null) {
                const passwordFeedbackClasses = passwordFeedback.classList;
                let passwordFeedbackClasses2 = passwordFeedback2.classList;
                // check if the first email is correct
                if (checkIfIncorrect(passwordFeedbackClasses)) {
                    passwordFeedbackClasses2.value = incorrectClass;
                    passwordFeedback2.innerText = "Please enter a secure password above first.";
                }
                // compare email input values
                else if (passwordOne !== passwordTwo) {
                    passwordFeedbackClasses2.value = incorrectClass;
                    passwordFeedback2.innerText = "Sorry, passwords do not match.";
                }
                else {
                    passwordFeedbackClasses2.value = correctClass;
                    passwordFeedback2.innerText = "Thank you, passwords do match.";
                }
            }
        }
        evaluateButton();
    }, 500);
}
function passwordFeedback() {
    let passwordFeedback = document.getElementById("password-feedback1");
    const passwordEntered = document.getElementById("password-input1").value;
    if (passwordEntered.length < 1)
        return;
    const passwordQuality = checkPasswordQuality(passwordEntered);
    if (passwordFeedback == null)
        return;
    if (passwordQuality.includes("Secure")) {
        passwordFeedback.innerText = `${passwordQuality} password, well done!`;
        passwordFeedback.classList.value = correctClass;
    }
    else if (passwordQuality.includes("Good")) {
        passwordFeedback.innerText = `${passwordQuality} password, thank you.`;
        passwordFeedback.classList.value = correctClass;
    }
    else if (passwordQuality.includes("Weak")) {
        passwordFeedback.innerText = `${passwordQuality} password, spicy it up please!`;
        passwordFeedback.classList.value = incorrectClass;
    }
    else {
        passwordFeedback.innerText = `${passwordQuality} password, improve it please!`;
        passwordFeedback.classList.value = incorrectClass;
    }
    comparePasswords();
}
function evaluateButton() {
    let feedbacks = [];
    const emailClasses1 = document.getElementById("email-feedback");
    const emailClasses2 = document.getElementById("email-feedback2");
    const nameClasses = document.getElementById("name-feedback");
    const passClasses1 = document.getElementById("password-feedback1");
    const passClasses2 = document.getElementById("password-feedback2");
    if (emailClasses1 != null && emailClasses2 != null && nameClasses != null && passClasses1 != null && passClasses2 != null) {
        feedbacks.push(String(emailClasses1.classList), String(emailClasses2.classList), String(nameClasses.classList), String(passClasses1.classList), String(passClasses2.classList));
    }
    const incorrectFields = feedbacks.filter(checkIfIncorrect);
    const signUpButton = document.getElementById("signup-button");
    if (incorrectFields.length === 0) {
        if (signUpButton != null) {
            signUpButton.disabled = false;
            signUpButton.classList.remove('cursor-not-allowed');
        }
    }
    else {
        signUpButton.disabled = true;
        signUpButton.classList.add('cursor-not-allowed');
    }
}
/*
* Helper functions
*
*/
// returns true if incorrect matches  / : string
function checkIfIncorrect(textValue) {
    return /^text-incorrect$/.test(textValue);
}
function checkPasswordQuality(pass) {
    const score = scorePassword(pass);
    if (score > 80)
        return "Secure";
    else if (score > 60)
        return "Good";
    else if (score >= 30)
        return "Weak";
    else
        return "Tragic";
}