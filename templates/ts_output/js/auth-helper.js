"use strict";
const emailInput = document.getElementById('email-input');
const inputFeedback = document.getElementById('email-feedback');
const passwordFeedbackOne = document.getElementById("password-feedback1");
const passwordFeedbackTwo = document.getElementById("password-feedback2");
const passwordInputOne = document.getElementById("password-input1");
const passwordInputTwo = document.getElementById("password-input2");
const submitButton = document.getElementById("submit-button");
function processEmailValue() {
    if (emailInput == null || inputFeedback == null)
        return;
    const emailPassed = emailInput.value;
    const returnValue = validateEmail(emailPassed);
    toggleSubmitButton(returnValue);
    return returnValue;
}
function validateEmail(address) {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,6})+$/.test(address)) {
        return true;
    }
    return false;
}
function parseEmail(textArg) {
    inputFeedback.classList.remove('hidden');
    if (textArg <= 5) {
        inputFeedback.innerText = 'Enter a valid email address.';
        return false;
    }
    let result = validateEmail(textArg);
    console.log(result);
    if (!result) {
        inputFeedback.innerText = 'Enter a valid email address.';
    }
    else {
        inputFeedback.innerText = 'Thank you for entering your email.';
        return true;
    }
}
function toggleSubmitButton(toEnable) {
    if (submitButton == null)
        return;
    if (toEnable) {
        if (submitButton.classList.contains('cursor-not-allowed')) {
            submitButton.disabled = false;
            submitButton.classList.remove('cursor-not-allowed');
        }
    }
    else {
        if (!submitButton.classList.contains('cursor-not-allowed')) {
            submitButton.disabled = true;
            submitButton.classList.add('cursor-not-allowed');
        }
    }
}
// CHECK PASSWORDS
function comparePasswords() {
    if (passwordInputOne == null || passwordInputTwo == null)
        return;
    const passwordOne = passwordInputOne.value;
    const passwordTwo = passwordInputTwo.value;
    // check if one of the passwords is not empty
    if (passwordOne.length !== 0 && passwordTwo.length !== 0) {
        if (passwordFeedbackOne != null && passwordFeedbackTwo != null) {
            passwordFeedbackTwo.classList.remove('hidden');
            // WARNING - includes is case-sensitive so make sure to match output of checkPasswordQuality()
            if (!passwordFeedbackOne.innerText.includes("Good") && !passwordFeedbackOne.innerText.includes("Secure")) {
                passwordFeedbackTwo.innerText = "Please enter a secure password above first.";
            }
            // compare email input values
            else if (passwordOne !== passwordTwo) {
                passwordFeedbackTwo.innerText = "Sorry, passwords do not match.";
            }
            else {
                passwordFeedbackTwo.innerText = "Thank you, passwords do match.";
                toggleSubmitButton(true);
            }
        }
    }
}
function getPasswordFeedback() {
    //TODO: Should be really dependenent on whether you are in login or sign up
    toggleSubmitButton(false);
    passwordFeedbackOne.classList.remove('hidden');
    const passwordEntered = document.getElementById("password-input1").value;
    if (passwordEntered.length < 1)
        return;
    const passwordQuality = checkPasswordQuality(passwordEntered);
    if (passwordFeedbackOne == null)
        return;
    if (passwordQuality.includes("Secure")) {
        passwordFeedbackOne.innerText = `${passwordQuality} password, well done!`;
    }
    else if (passwordQuality.includes("Good")) {
        passwordFeedbackOne.innerText = `${passwordQuality} password, thank you.`;
    }
    else if (passwordQuality.includes("Weak")) {
        passwordFeedbackOne.innerText = `${passwordQuality} password, spicy it up please!`;
    }
    else {
        passwordFeedbackOne.innerText = `${passwordQuality} password, improve it please!`;
    }
    if (!passwordFeedbackTwo.classList.contains('hidden')) {
        passwordFeedbackTwo.classList.add('hidden');
    }
    //comparePasswords()
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
/*
* Used
* https://stackoverflow.com/questions/948172/password-strength-meter#comment120524342_11268104
* */
function scorePassword(pass) {
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
