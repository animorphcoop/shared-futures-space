let selectedTags: Array<HTMLElement> = []

function selectTag(tagElemId: string, tagName: string) {
    console.log(tagElemId)
    console.log(tagName)

    //let currentResourceElem = document.getElementById(tagElemId)
    //console.log(currentResourceElem)

    const currentTagElem = document.getElementById(tagElemId)
    if (currentTagElem == null || selectedTags == null) return
    if (!selectedTags.includes(currentTagElem)) {
        console.log('new')
        currentTagElem.classList.add("bg-purple/25")
        selectedTags.push(currentTagElem)

    } else {
        console.log('removing')
        console.log(selectedTags.length)

        currentTagElem.classList.remove("bg-purple/25")
        selectedTags.forEach((item, index) => {
            if (item === currentTagElem)
                selectedTags.splice(index, 1)
        })
        console.log(selectedTags.length)
    }


    //console.log(selectedTags[0])
    console.log('hehehe6')
}
