import { expose } from "@/templates/ts/utils.ts"

/*
TODO(NS): looks like this variables are not used anywhere, but I'll leave them here for now

const visible: string = 'block'
const hidden: string = 'hidden'

const initial = document.getElementById("initial-list")
const results = document.getElementById("search-results")

const order_by = <HTMLElement>document.getElementById("orderby")

let flipped: boolean = false
*/

const searchbar = <HTMLInputElement>document.getElementById("searchbar")

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

expose({ buttonTagSearch, setResultCount })