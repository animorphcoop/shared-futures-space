"use strict";
const emailInput = document.getElementById('email-input');
//input?.addEventListener('change', updateValue)
const inputFeedback = document.getElementById('email-feedback');
const submitButton = document.getElementById("submit-button");
function processEmailValue() {
    if (emailInput == null || inputFeedback == null || submitButton == null)
        return;
    const emailPassed = emailInput.value;
    // console.log(ValidateEmail(ev.target.value))
    if (!validateEmail(emailPassed)) {
        if (inputFeedback.classList.contains('hidden')) {
            inputFeedback.classList.remove('hidden');
        }
        if (!submitButton.classList.contains('cursor-not-allowed')) {
            submitButton.disabled = true;
            submitButton.classList.add('cursor-not-allowed');
        }
        return false;
    }
    else {
        if (!inputFeedback.classList.contains('hidden')) {
            inputFeedback.classList.add('hidden');
        }
        if (submitButton.classList.contains('cursor-not-allowed')) {
            submitButton.disabled = false;
            submitButton.classList.remove('cursor-not-allowed');
        }
        return true;
    }
}
function emailFeedback() {
    //const val: string = input.value
    //inputFeedback.innerText = val
    // console.log(ValidateEmail(ev.target.value))
    /*    if (!validateEmail((ev.target as HTMLInputElement).value)) {
            if (inputFeedback.classList.contains('hidden')) {
                inputFeedback.classList.remove('hidden')
            }
            if (!submitButton.classList.contains('cursor-not-allowed')) {
                submitButton.disabled = true
                submitButton.classList.add('cursor-not-allowed')
            }

        } else {
            if (!inputFeedback.classList.contains('hidden')) {
                inputFeedback.classList.add('hidden')
            }
            if (submitButton.classList.contains('cursor-not-allowed')) {
                submitButton.disabled = false
                submitButton.classList.remove('cursor-not-allowed')
            }
        }*/
}
/*function parseEmail(textInput: string) {
/!*    if (textInput.length <= 5) {
        setTimeout(() => {
            inputFeedback.classList.remove('hidden')
            inputFeedback.innerText = 'too short'
            return false
        }, 500)
    } else {
        console.log('KIDDING')
        inputFeedback.innerText = 'long enough short'
    }*!/

    let result = validateEmail(textInput)
    console.log(result)
    if (!result){
            inputFeedback.classList.remove('hidden')
            //inputFeedback.innerText = 'Enter a valid email address.'
    }
    return result


}*/
function validateEmail(address) {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,6})+$/.test(address)) {
        return true;
    }
    return false;
}