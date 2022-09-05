"use strict";
const input = document.getElementById('email-input');
input === null || input === void 0 ? void 0 : input.addEventListener('change', updateValue);
const inputFeedback = document.getElementById('email-feedback');
const submitButton = document.getElementById("submit-button");
function updateValue(ev) {
    if (!ev.target || inputFeedback == null || submitButton == null)
        return;
    // console.log(ValidateEmail(ev.target.value))
    if (!ValidateEmail(ev.target.value)) {
        if (inputFeedback.classList.contains('hidden')) {
            inputFeedback.classList.remove('hidden');
        }
        if (!submitButton.classList.contains('cursor-not-allowed')) {
            submitButton.disabled = true;
            submitButton.classList.add('cursor-not-allowed');
        }
    }
    else {
        if (!inputFeedback.classList.contains('hidden')) {
            inputFeedback.classList.add('hidden');
        }
        if (submitButton.classList.contains('cursor-not-allowed')) {
            submitButton.disabled = false;
            submitButton.classList.remove('cursor-not-allowed');
        }
    }
}
function ValidateEmail(address) {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,6})+$/.test(address)) {
        return true;
    }
    return false;
}
