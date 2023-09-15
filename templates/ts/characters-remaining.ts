import Alpine from "alpinejs";

/**
 * A thing to print the characters remaining, usage guide:
 *
 *    <input type="text" id="foo" maxlength="200">
 *    <span x-characters-remaining="#foo"></span> characters remaining
 *
 *    Will show: "200/200 characters remaining"
 */
Alpine.directive('characters-remaining', (messageEl, { expression }, { cleanup }) => {
    const inputSelector = expression
    const el: HTMLInputElement | null = document.querySelector(inputSelector)

    if (!el) {
        console.warn('used x-characters-remaining but input element not found using selector: ' + inputSelector)
        return
    }

    const inputEl = el
    const maxLength = inputEl.maxLength

    if (inputEl) {
        writeCharactersRemaining()

        function onInput () {
            writeCharactersRemaining()
        }

        function writeCharactersRemaining () {
            const currentLength = inputEl.value.length
            const remaining = maxLength - currentLength
            messageEl.innerHTML = `${remaining}/${maxLength}`
        }

        inputEl.addEventListener('input', onInput)
        cleanup(() => {
            inputEl.removeEventListener('input', onInput)
        })
    }
})