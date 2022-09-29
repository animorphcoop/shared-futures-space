"use strict";
let avatarClicked;
const avatarInputChange = document.getElementById("avatar");
function toggleAvatar() {
    const avatars = document.getElementById("avatar-list");
    if (avatars == null)
        return;
    avatars.classList.toggle('hidden');
}
function changeAvatar(avatarElemId, avatarPk) {
    console.log(avatarPk);
    if (avatarClicked != null) {
        avatarClicked.classList.remove("bg-purple-600");
    }
    const currentAvatarElem = document.getElementById(avatarElemId);
    if (currentAvatarElem == null)
        return;
    currentAvatarElem.classList.add("bg-purple-600");
    avatarClicked = currentAvatarElem;
    if (avatarInputChange == null)
        return;
    avatarInputChange.setAttribute('value', avatarPk);
}
