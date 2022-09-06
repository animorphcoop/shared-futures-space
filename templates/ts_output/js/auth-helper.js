"use strict";
const emailInput = document.getElementById('email-input');
//input?.addEventListener('change', updateValue)
const inputFeedback = document.getElementById('email-feedback');
const submitButton = document.getElementById("submit-button");
function processEmailValue() {
    if (emailInput == null || inputFeedback == null || submitButton == null)
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
        return true;
    }
}
function toggleSubmitButton(toEnable) {
    if (toEnable) {
        if (!inputFeedback.classList.contains('hidden')) {
            inputFeedback.classList.add('hidden');
        }
        if (submitButton.classList.contains('cursor-not-allowed')) {
            submitButton.disabled = false;
            submitButton.classList.remove('cursor-not-allowed');
        }
    }
    else {
        if (inputFeedback.classList.contains('hidden')) {
            inputFeedback.classList.remove('hidden');
        }
        if (!submitButton.classList.contains('cursor-not-allowed')) {
            submitButton.disabled = true;
            submitButton.classList.add('cursor-not-allowed');
        }
    }
}
// CHECK PASSWORDS
function comparePasswords() {
    const passwordFeedback = document.getElementById("password-feedback1");
    const passwordFeedback2 = document.getElementById("password-feedback2");
    const passwordOne = document.getElementById("password-input1").value;
    const passwordTwo = document.getElementById("password-input2").value;
    // check if one of the passwords is not empty
    if (passwordOne.length !== 0 && passwordTwo.length !== 0) {
        if (passwordFeedback != null && passwordFeedback2 != null) {
            const passwordFeedbackClasses = passwordFeedback.classList;
            let passwordFeedbackClasses2 = passwordFeedback2.classList;
            if (passwordOne !== passwordTwo) {
                //passwordFeedbackClasses2.value = incorrectClass
                passwordFeedback2.innerText = "Sorry, passwords do not match.";
            }
            else {
                //passwordFeedbackClasses2.value = correctClass
                passwordFeedback2.innerText = "Thank you, passwords do match.";
            }
        }
    }
}
function passwordFeedback() {
    console.log('triggering this');
    let passwordFeedback = document.getElementById("password-feedback1");
    const passwordEntered = document.getElementById("password-input1").value;
    if (passwordEntered.length < 1)
        return;
    const passwordQuality = checkPasswordQuality(passwordEntered);
    if (passwordFeedback == null)
        return;
    if (passwordQuality.includes("Secure")) {
        passwordFeedback.innerText = `${passwordQuality} password, well done!`;
        // passwordFeedback.classList.value = correctClass
    }
    else if (passwordQuality.includes("Good")) {
        passwordFeedback.innerText = `${passwordQuality} password, thank you.`;
        // passwordFeedback.classList.value = correctClass
    }
    else if (passwordQuality.includes("Weak")) {
        passwordFeedback.innerText = `${passwordQuality} password, spicy it up please!`;
        // passwordFeedback.classList.value = incorrectClass
    }
    else {
        passwordFeedback.innerText = `${passwordQuality} password, improve it please!`;
        //passwordFeedback.classList.value = incorrectClass
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
