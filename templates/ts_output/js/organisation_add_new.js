"use strict";
const organisationDataEnter = document.getElementById("organisation-name-enter");
function uncoverNewOrgTyping() {
    if (organisationDataEnter == null)
        return;
    organisationDataEnter.classList.remove('hidden');
}
function addName() {
    if (organisationDataEnter == null)
        return;
    const tempOrgNameInput = document.getElementById("organisation-name");
    const tempOrgUrlInput = document.getElementById("organisation-url");
    if (tempOrgNameInput == null || tempOrgUrlInput == null)
        return;
    const newOrgName = tempOrgNameInput.value;
    const newOrgUrl = tempOrgUrlInput.value;
    selectOrganisation(newOrgName, newOrgUrl);
    submitOrganisation();
    organisationDataEnter.classList.add('hidden');
}
