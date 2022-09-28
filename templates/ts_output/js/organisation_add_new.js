"use strict";
const organisationDataEnter = document.getElementById("organisation-name-enter");
function uncoverNewOrgTyping(toOpenInput) {
    if (organisationDataEnter == null || organisationList == null)
        return;
    if (toOpenInput) {
        organisationDataEnter.classList.remove('hidden');
    }
    else {
        organisationDataEnter.classList.add('hidden');
    }
}
function addName() {
    if (organisationDataEnter == null)
        return;
    const errorBoxName = document.getElementById("error-box-name");
    const tempOrgNameInput = document.getElementById("organisation-name");
    const tempOrgUrlInput = document.getElementById("organisation-url");
    if (tempOrgNameInput == null || tempOrgUrlInput == null || errorBoxName == null)
        return;
    if (tempOrgNameInput.value.length < 1) {
        if (errorBoxName.classList.contains('hidden')) {
            errorBoxName.classList.remove('hidden');
        }
        tempOrgNameInput.setAttribute("required", "");
        return;
    }
    if (!errorBoxName.classList.contains('hidden')) {
        errorBoxName.classList.add('hidden');
    }
    const newOrgName = tempOrgNameInput.value;
    const newOrgUrl = tempOrgUrlInput.value;
    selectOrganisation(newOrgName, newOrgUrl);
    submitOrganisation();
    organisationDataEnter.classList.add('hidden');
}
