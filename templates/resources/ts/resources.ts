const visible: string = 'block'
const hidden: string = 'hidden'

const initial = document.getElementById("initial-list")
const results = document.getElementById("search-results")

const searchbar = <HTMLInputElement>document.getElementById("searchbar")
const order_by = <HTMLElement>document.getElementById("orderby")

let flipped: boolean = false

function buttonTagSearch(tag: string) {
    searchbar.value = tag
    //console.log('search')
    //searching(true)
}

function setResultCount(count: number) {
    let elem = document.getElementById("result-count");
    if (elem != null) {
        if (count == 1) {
            elem.innerHTML = count.toString() + " result available";
        } else {
            elem.innerHTML = count.toString() + " results available";
        }
    }
}

