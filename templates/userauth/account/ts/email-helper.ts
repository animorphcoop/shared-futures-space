const input = (<HTMLInputElement>document.getElementById('email-input'))
input?.addEventListener('change', updateValue)

const inputFeedback: HTMLElement | null = document.getElementById('email-feedback')
const submitButton: HTMLButtonElement = <HTMLButtonElement>document.getElementById("submit-button")

function updateValue(ev: Event) {
    if (!ev.target || inputFeedback == null || submitButton == null) return

    // console.log(ValidateEmail(ev.target.value))
    if (!ValidateEmail((ev.target as HTMLInputElement).value)) {
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
    }
}

function ValidateEmail(address: string) {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,6})+$/.test(address)) {
        return true
    }
    return false
}
