let lastClicked: HTMLElement | null

const avatarInput = (<HTMLInputElement>document.getElementById("avatar"))


function toggleAvatar() {
    const avatars = document.getElementById("avatar-list")
    avatars.classList.toggle('hidden')

}

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
