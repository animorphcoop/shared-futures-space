"use strict";
let selectedOrganisation = '';
let newOrganisationUrl = '';
const organisationCheckboxBlock = document.getElementById("organisation-starter");
const checkbox = document.getElementById("organisation-checkbox");
const organisationDataBlock = document.getElementById("organisation-data");
const organisationList = document.getElementById("organisation-list");
const organisationNameInput = document.getElementById("organisation_name");
const organisationUrlInput = document.getElementById("organisation_url");
function toggleOrganisations() {
    if (checkbox == null || organisationDataBlock == null || selectedOrganisation == null || organisationList == null)
        return;
    if (checkbox.checked) {
        organisationList.classList.remove('hidden');
    }
    else {
        organisationList.classList.add('hidden');
        organisationDataBlock.classList.add('hidden');
        selectedOrganisation = 'None';
        organisationNameInput.value = selectedOrganisation;
    }
}
function backFromOrganisations() {
    if (organisationList == null || checkbox == null || organisationNameInput == null || organisationDataBlock == null || organisationCheckboxBlock == null)
        return;
    if (checkbox.checked) {
        organisationList.classList.add('hidden');
        checkbox.checked = false;
        selectedOrganisation = 'None';
        organisationNameInput.value = selectedOrganisation;
        organisationDataBlock.classList.add('hidden');
        if (organisationCheckboxBlock.classList.contains('hidden')) {
            organisationCheckboxBlock.classList.remove('hidden');
        }
    }
}
function selectOrganisation(orgName, orgUrl) {
    selectedOrganisation = orgName;
    newOrganisationUrl = orgUrl;
}
function submitOrganisation() {
    if (organisationNameInput == null || organisationDataBlock == null || organisationList == null || organisationUrlInput == null)
        return;
    organisationNameInput.value = selectedOrganisation;
    organisationNameInput.classList.add('cursor-not-allowed');
    organisationUrlInput.value = newOrganisationUrl;
    organisationDataBlock.classList.remove('hidden');
    organisationList.classList.add('hidden');
}
function openAddName() {
    if (organisationNameInput == null || organisationDataBlock == null || organisationList == null)
        return;
    organisationList.classList.add('hidden');
    uncoverNewOrgTyping(true);
}
function goBack() {
    if (organisationList == null)
        return;
    organisationList.classList.remove('hidden');
    uncoverNewOrgTyping(false);
}