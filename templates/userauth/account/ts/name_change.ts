const nameContainer: HTMLElement | null = document.getElementById("name-change")
const nameChangeInput = (<HTMLInputElement>document.getElementById("display_name"))


function toggleNameChange() {
    if (nameContainer == null) return
    nameContainer.classList.toggle('hidden')
}

function validateName() {
    if (nameChangeInput == null) return

    let errorCount = 0
    if (nameChangeInput.value.length < 1) {
        nameChangeInput.setAttribute("required", "");
        errorCount++
    } else {
        toggleNameChange();
    }
    return errorCount === 0
}