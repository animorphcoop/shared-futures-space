import { expose } from "@/templates/ts/utils.ts"

const postcodeContainer: HTMLElement | null = document.getElementById("postcode-change")
const postcodeChangeInput = (<HTMLInputElement>document.getElementById("postcode"))


function togglePostcodeChange() {
    if (postcodeContainer == null) return
    postcodeContainer.classList.toggle('hidden')
}

function validatePostcode() {
    if (postcodeChangeInput == null) return

    let errorCount = 0
    if (postcodeChangeInput.value.length < 1) {
        postcodeChangeInput.setAttribute("required", "");
        errorCount++
    } else {
        togglePostcodeChange();
    }
    return errorCount === 0
}

expose({
    togglePostcodeChange,
    validatePostcode,
})