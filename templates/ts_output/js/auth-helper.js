"use strict";
const emailInput = document.getElementById('email-input');
const inputFeedback = document.getElementById('email-feedback');
const passwordFeedbackOne = document.getElementById("password-feedback1");
const passwordFeedbackTwo = document.getElementById("password-feedback2");
const passwordInputOne = document.getElementById("password-input1");
const passwordInputTwo = document.getElementById("password-input2");
const submitButton = document.getElementById("submit-button");
// triggered from x-init on the form
function setupObservers() {
    console.log('init');
    //TODO: Have 3 observers and they trigger a method that collates results from the 3 existing ones, then unlock the button and skip checkFeedbackBeforeSubmit dodgy method
    const observerEmail = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            if (inputFeedback.innerText === '') {
                console.log('empty email');
                if (!inputFeedback.classList.contains('hidden')) {
                    inputFeedback.classList.add('hidden');
                    evaluateButton();
                }
            }
            else {
                if (inputFeedback.classList.contains('hidden')) {
                    inputFeedback.classList.remove('hidden');
                }
            }
            console.log(inputFeedback.innerText);
        });
    });
    let configEmail = { childList: true };
    observerEmail.observe(inputFeedback, configEmail);
    const observerPasswordOne = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            if (passwordFeedbackOne.innerText === '') {
                console.log('empty pass1');
                if (!passwordFeedbackOne.classList.contains('hidden')) {
                    passwordFeedbackOne.classList.add('hidden');
                    evaluateButton();
                }
            }
            else {
                if (passwordFeedbackOne.classList.contains('hidden')) {
                    passwordFeedbackOne.classList.remove('hidden');
                }
            }
            console.log(passwordFeedbackOne.innerText);
        });
    });
    let configPasswordOne = { childList: true };
    observerPasswordOne.observe(passwordFeedbackOne, configPasswordOne);
    const observerPasswordTwo = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            if (passwordFeedbackTwo.innerText === '') {
                console.log('empty pass 2');
                console.log(passwordFeedbackTwo.classList.contains('hidden'));
                if (!passwordFeedbackTwo.classList.contains('hidden')) {
                    passwordFeedbackTwo.classList.add('hidden');
                    evaluateButton();
                }
            }
            else {
                if (passwordFeedbackTwo.classList.contains('hidden')) {
                    passwordFeedbackTwo.classList.remove('hidden');
                }
            }
            console.log(passwordFeedbackTwo.innerText);
        });
    });
    let configPasswordTwo = { childList: true };
    observerPasswordTwo.observe(passwordFeedbackTwo, configPasswordTwo);
}
//TODO: ADD DELAY
function evaluateButton() {
    if (inputFeedback.innerText === '' && passwordFeedbackOne.innerText === '' && passwordFeedbackTwo.innerText === '') {
        toggleSubmitButton(true);
    }
    else {
        toggleSubmitButton(false);
    }
}
function processEmailValue() {
    //let inputFeedback: HTMLElement | null = document.getElementById('email-feedback')
    if (emailInput == null || inputFeedback == null)
        return;
    const emailPassed = emailInput.value;
    if (emailPassed.length <= 5) {
        inputFeedback.innerText = 'Please enter a valid email address.';
        return false;
    }
    else {
        const returnValue = validateEmail(emailPassed);
        if (!returnValue) {
            inputFeedback.innerText = 'Please enter a valid email address.';
            return false;
        }
        else {
            inputFeedback.innerText = '';
            return true;
        }
    }
}
function validateEmail(address) {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,6})+$/.test(address)) {
        return true;
    }
    return false;
}
function toggleSubmitButton(toEnable) {
    if (submitButton == null)
        return;
    if (toEnable) {
        if (submitButton.classList.contains('cursor-not-allowed')) {
            submitButton.classList.remove('cursor-not-allowed');
            submitButton.disabled = false;
        }
    }
    else {
        if (!submitButton.classList.contains('cursor-not-allowed')) {
            submitButton.classList.add('cursor-not-allowed');
            submitButton.disabled = true;
        }
    }
}
function comparePasswords() {
    if (passwordInputOne == null || passwordInputTwo == null)
        return;
    const passwordOne = passwordInputOne.value;
    const passwordTwo = passwordInputTwo.value;
    // check if one of the passwords is not empty
    if (passwordOne.length !== 0 && passwordTwo.length !== 0) {
        if (passwordFeedbackOne != null && passwordFeedbackTwo != null) {
            if (passwordFeedbackOne.innerText !== '') {
                passwordFeedbackTwo.innerText = 'Please enter a secure password above first.';
            }
            else if (passwordOne !== passwordTwo) {
                passwordFeedbackTwo.innerText = 'Sorry, passwords do not match.';
            }
            else {
                passwordFeedbackTwo.innerText = '';
            }
        }
    }
}
function getPasswordFeedback() {
    if (passwordFeedbackOne != null && passwordFeedbackTwo != null) {
        //TODO: Should be really dependent on whether you are in login or sign up
        //toggleSubmitButton(false)
        //passwordFeedbackOne.classList.remove('hidden')
        const passwordEntered = document.getElementById("password-input1").value;
        if (passwordEntered.length < 1)
            return;
        const passwordQuality = checkPasswordQuality(passwordEntered);
        if (passwordQuality.includes("Secure") || passwordQuality.includes("Good")) {
            passwordFeedbackOne.innerText = '';
        }
        else {
            passwordFeedbackOne.innerText = 'Please improve your password!';
        }
        comparePasswords();
    }
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
