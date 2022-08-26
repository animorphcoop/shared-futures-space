const visible: string = 'block'
const hidden: string = 'hidden'

const initial = document.getElementById("initial-list")
const results = document.getElementById("search-results")

const searchbar = <HTMLInputElement>document.getElementById("searchbar")

console.log('alive')
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
    console.log('wtf')
    console.log(initial)
    console.log(results)

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

// dummy method, always returns true to resolve issue with input field normally calling the results we need tags on the list & search partials to do the same.
//TODO: Improve, abstract
function resultsTrigger() {
    flipped = false
    results.innerHTML = ''
    searching(true)
    return true
}