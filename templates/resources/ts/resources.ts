const visible: string = 'block'
const hidden: string = 'hidden'

const initial = document.getElementById("initial-list")
const results = document.getElementById("search-results")

const searchbar = <HTMLInputElement>document.getElementById("searchbar")
const order_by = <HTMLElement>document.getElementById("orderby")

let flipped: boolean = false

/*
order_by.addEventListener('input', function (evt) {
    if (flipped) {
        searching(true);
    } else {
        
    }
}

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
*/
function buttonTagSearch(tag: string) {
    searchbar.value = tag
    console.log('search')
    //searching(true)
}
