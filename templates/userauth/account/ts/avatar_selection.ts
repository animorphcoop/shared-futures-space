import { expose } from "@/templates/ts/utils.ts"

let avatarClicked: HTMLElement | null

const avatarInputChange = (<HTMLInputElement>document.getElementById("avatar"))


function toggleAvatar() {
    const avatars = document.getElementById("avatar-list")
    if (avatars == null) return
    avatars.classList.toggle('hidden')

}

function changeAvatar(avatarElemId: string, avatarPk: string) {
    if (avatarClicked != null) {
        avatarClicked.classList.remove("bg-purple/25")
    }
    const currentAvatarElem = document.getElementById(avatarElemId)
    if (currentAvatarElem == null) return

    currentAvatarElem.classList.add("bg-purple/25")
    avatarClicked = currentAvatarElem

    if (avatarInputChange == null) return
    avatarInputChange.setAttribute('value', avatarPk)

}

expose({
    changeAvatar,
    toggleAvatar,
})