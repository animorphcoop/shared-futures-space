import { expose } from "@/templates/ts/utils.ts"

let selectedTags: Array<HTMLElement> = []
let counterValue: number = 3
const tagCounterElem: HTMLElement | null = document.getElementById("counter")
const tagsInput = (<HTMLInputElement>document.getElementById("tags_input"))

expose({ selectTag })

function selectTag(tagElemId: string, tagName: string) {

    const currentTagElem = document.getElementById(tagElemId)
    if (currentTagElem == null || selectedTags == null || tagsInput == null) return

    if (!selectedTags.includes(currentTagElem)) {
        if (counterValue > 0) {
            currentTagElem.classList.add("bg-green-pale")
            selectedTags.push(currentTagElem)

            if (tagsInput.value == "") {
                tagsInput.value = `"${tagName}",`
            } else {
                tagsInput.value = `${tagsInput.value} "${tagName}", `
            }

            counterDown(true)
        }

    } else {
        if (counterValue < 3) {
            currentTagElem.classList.remove("bg-green-pale")
            selectedTags.forEach((item, index) => {
                if (item === currentTagElem)
                    selectedTags.splice(index, 1)
            })
            if (tagsInput.value != "") {
                let toRemove = `"${tagName}",`
                tagsInput.value = tagsInput.value.replace(toRemove, "")

            }

            counterDown(false)

        }
    }

}

function counterDown(toDecrease: boolean) {

    if (tagCounterElem == null || counterValue == null) return

    if (toDecrease) {
        counterValue--
    } else {
        counterValue++
    }


    if (counterValue < 1) {
        if (!tagCounterElem.classList.contains('hidden')) {
            tagCounterElem.classList.add('hidden')
        }
    } else {

        if (tagCounterElem.classList.contains('hidden')) {
            tagCounterElem.classList.remove('hidden')
        }
    }
    tagCounterElem.innerText = `choose ${counterValue}`


}
