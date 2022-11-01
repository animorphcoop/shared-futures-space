"use strict";
let selectedTags = [];
let counterValue = 3;
const tagCounterElem = document.getElementById("counter");
function selectTag(tagElemId, tagName) {
    console.log(tagElemId);
    console.log(tagName);
    const currentTagElem = document.getElementById(tagElemId);
    if (currentTagElem == null || selectedTags == null)
        return;
    if (!selectedTags.includes(currentTagElem)) {
        console.log('new');
        if (counterValue > 0) {
            currentTagElem.classList.add("bg-purple/25");
            selectedTags.push(currentTagElem);
            counterDown(true);
        }
    }
    else {
        console.log('removing');
        console.log(selectedTags.length);
        if (counterValue < 3) {
            currentTagElem.classList.remove("bg-purple/25");
            selectedTags.forEach((item, index) => {
                if (item === currentTagElem)
                    selectedTags.splice(index, 1);
            });
            counterDown(false);
        }
        console.log(selectedTags.length);
    }
    //console.log(selectedTags[0])
    console.log('hehehe6');
}
function counterDown(toDecrease) {
    if (tagCounterElem == null || counterValue == null)
        return;
    if (toDecrease) {
        counterValue--;
    }
    else {
        counterValue++;
    }
    console.log(counterValue);
    if (counterValue < 1) {
        if (!tagCounterElem.classList.contains('hidden')) {
            tagCounterElem.classList.add('hidden');
        }
    }
    else {
        if (tagCounterElem.classList.contains('hidden')) {
            tagCounterElem.classList.remove('hidden');
        }
    }
    console.log(tagCounterElem.classList);
    tagCounterElem.innerText = `choose ${counterValue}`;
}
