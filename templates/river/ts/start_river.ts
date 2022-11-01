function selectTag(tagElemId: string, tagName: string) {
    console.log(tagElemId)
    console.log(tagName)

    //let currentResourceElem = document.getElementById(tagElemId)
    //console.log(currentResourceElem)

    const currentTagElem = document.getElementById(tagElemId)
    if (currentTagElem == null) return
    currentTagElem.classList.add("bg-purple/25")
}
