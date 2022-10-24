function swapHearts(buttonText: string) {
    const heart = document.getElementById('heart-icon')
    if (heart == null) return
    if (buttonText.includes("SAVED")) {
        if (heart.classList.contains('hidden')) {
            heart.classList.remove('hidden')
        }

    } else {
        if (!heart.classList.contains('hidden')) {
            heart.classList.add('hidden')
        }
    }
}