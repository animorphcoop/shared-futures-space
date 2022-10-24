function swapHearts(buttonText: string, heartId: string) {
    console.log(buttonText)
    console.log(heartId)
    const heart = document.getElementById(heartId)
    if (heart == null) return
    if (buttonText.includes("SAVED")) {
        heart.innerText = 'saved'
        console.log('HIGHLIGHT')
    } else {
        heart.innerText = 'not saved'
        console.log('NOT')

    }

}