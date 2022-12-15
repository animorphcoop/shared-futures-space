"use strict";
const visible = 'block';
const hidden = 'hidden';
const initial = document.getElementById("initial-list");
const results = document.getElementById("search-results");
const searchbar = document.getElementById("searchbar");
const order_by = document.getElementById("orderby");
let flipped = false;
function buttonTagSearch(tag) {
    searchbar.value = tag;
    //console.log('search')
    //searching(true)
}
function setResultCount(count) {
    let elem = document.getElementById("result-count");
    if (elem != null) {
        if (count == 1) {
            elem.innerHTML = count.toString() + " result available";
        }
        else {
            elem.innerHTML = count.toString() + " results available";
        }
    }
}
