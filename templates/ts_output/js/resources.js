"use strict";
const visible = 'block';
const hidden = 'hidden';
const initial = document.getElementById("initial-list");
const results = document.getElementById("search-results");
const searchbar = document.getElementById("searchbar");
let flipped = false;
searchbar.addEventListener('input', function (evt) {
    if (searchbar.value.length > 2) {
        searching(true);
    }
    else {
        flipped = false;
        searching(false);
    }
});
function searching(displayResults) {
    if (initial != null && results != null) {
        if (!flipped) {
            if (displayResults) {
                initial.classList.value = hidden;
                results.classList.value = visible;
                flipped = true;
            }
            else {
                initial.classList.value = visible;
                results.classList.value = hidden;
                results.innerHTML = '';
            }
        }
    }
}
