let lastClicked = null

function selectAvatar(avatarElemId, avatarPk) {
    console.log(avatarPk)
    if (lastClicked != null) {
        lastClicked.classList.remove("bg-purple-600")
    }
    document.getElementById(avatarElemId).classList.add("bg-purple-600")

    lastClicked = document.getElementById(avatarElemId)

    let avatarFormInput = document.getElementById("avatar")
    avatarFormInput.setAttribute('value', avatarPk)

}