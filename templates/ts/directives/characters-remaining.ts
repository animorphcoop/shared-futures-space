import Alpine from "alpinejs";

/**
 * A directive to print the characters remaining, usage guide:
 *
 *    <input id="foo" type="text" maxlength="200">
 *    <span x-characters-remaining="#foo"></span> characters remaining
 *
 * This will show: "200/200 characters remaining" and update as you type.
 */
Alpine.directive('characters-remaining', (
    messageEl,
    { expression }, { cleanup },
) => {
    // we use the provided expression as a css selector for the input
    const inputSelector = expression
    const el: HTMLInputElement | null = document.querySelector(inputSelector)

    if (!el) {
        console.warn('used x-characters-remaining but input element not found using selector: ' + inputSelector)
        return
    }

    const inputEl = el
    const maxLength = inputEl.maxLength

    if (!maxLength) {
        console.warn('used x-characters-remaining but input element does not have maxLength attribute')
        return
    }

    // Initial values
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
})