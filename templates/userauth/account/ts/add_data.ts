let lastClicked: HTMLElement | null

const addDataForm: HTMLFormElement = (<HTMLFormElement>document.getElementById("add-data-form"))
const nameInput = (<HTMLInputElement>document.getElementById("display_name"))
const yearOfBirthInput = (<HTMLInputElement>document.getElementById("year_of_birth"))
const postcodeInput = (<HTMLInputElement>document.getElementById("post_code"))

const avatarInput = (<HTMLInputElement>document.getElementById("avatar"))

const errorBox: HTMLElement | null = document.getElementById("error-box")

function selectAvatar(avatarElemId: string, avatarPk: string) {
    console.log(avatarPk)

    if (lastClicked != null) {
        lastClicked.classList.remove("bg-purple-600")
    }
    const currentAvatarElem = document.getElementById(avatarElemId)
    if (currentAvatarElem == null) return

    currentAvatarElem.classList.add("bg-purple-600")
    lastClicked = currentAvatarElem

    if (avatarInput == null) return
    avatarInput.setAttribute('value', avatarPk)

}

function validateFields() {

    if (nameInput == null || yearOfBirthInput == null || postcodeInput == null || addDataForm == null || errorBox == null) return

    if (nameInput.value.length < 1 || yearOfBirthInput.value.length < 1 || postcodeInput.value.length < 1) {
        console.log('empty innit')
        if (errorBox.classList.contains('hidden')) {
            errorBox.classList.remove('hidden')
        }
        if (nameInput.value.length < 1) {
            nameInput.setAttribute("required", "");
        }
        if (yearOfBirthInput.value.length < 1) {
            yearOfBirthInput.setAttribute("required", "");
        }
        if (postcodeInput.value.length < 1) {
            postcodeInput.setAttribute("required", "");
        }



    } else {
        if (!errorBox.classList.contains('hidden')) {
            errorBox.classList.add('hidden');
        }
        console.log('airght form')

        addDataForm.submit()
    }


}