const visible: string = 'block'
const hidden: string = 'hidden'

const initial = document.getElementById("initial")
const results = document.getElementById("results")

const searchbar = <HTMLInputElement>document.getElementById("searchbar")


let flipped: boolean = false


searchbar.addEventListener('input', function (evt) {
    if (searchbar.value.length > 2) {
        searching(true)
    } else {
        flipped = false
        searching(false)

    }

});

function searching(displayResults: boolean) {
    if (initial != null && results != null) {
        if (!flipped) {
            if (displayResults) {
                initial.classList.value = hidden
                results.classList.value = visible
                flipped = true
            } else {
                initial.classList.value = visible
                results.classList.value = hidden
                results.innerHTML = ''
            }
        }
    }


}