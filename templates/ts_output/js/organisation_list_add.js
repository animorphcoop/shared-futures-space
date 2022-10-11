"use strict";
let selectedOrganisation = '';
let newOrganisationUrl = '';
const organisationCheckboxBlock = document.getElementById("organisation-starter");
const checkbox = document.getElementById("organisation-checkbox");
const organisationDataBlock = document.getElementById("organisation-data");
const organisationList = document.getElementById("organisation-list");
const organisationNameInput = document.getElementById("organisation_name");
const organisationUrlInput = document.getElementById("organisation_url");
const stopBodyScroll = () => {
    const scrollY = document.documentElement.style.getPropertyValue('--scroll-y');
    const body = document.body;
    body.style.position = 'fixed';
    body.style.top = `-${scrollY}`;
};
const enableBodyScroll = () => {
    const body = document.body;
    const scrollY = body.style.top;
    body.style.position = '';
    body.style.top = '';
    window.scrollTo(0, parseInt(scrollY || '0') * -1);
};
window.addEventListener('scroll', () => {
    document.documentElement.style.setProperty('--scroll-y', `${window.scrollY}px`);
    console.log('live ' + scrollY);
});
function toggleOrganisationsAdd() {
    if (checkbox == null || organisationDataBlock == null || selectedOrganisation == null || organisationList == null)
        return;
    if (checkbox.checked) {
        organisationList.classList.remove('hidden');
        console.log('toggleOrganisationsAdd if checkbox.checked stopBodyScroll');
        stopBodyScroll();
    }
    else {
        console.log('toggleOrganisationsAdd checkbox.checked not enableBodyScroll');
        // enableBodyScroll();
        organisationList.classList.add('hidden');
        organisationDataBlock.classList.add('hidden');
        selectedOrganisation = 'None';
        organisationNameInput.value = selectedOrganisation;
    }
}
function toggleOrganisationsChange() {
    if (organisationDataBlock == null || selectedOrganisation == null || organisationList == null)
        return;
    organisationDataBlock.classList.remove('hidden');
    organisationList.classList.remove('hidden');
    console.log('toggleOrganisationsChange stopBodyScroll');
    stopBodyScroll();
    /*
        if (checkbox.checked) {
            organisationList.classList.remove('hidden')
        } else {
            organisationList.classList.add('hidden')
            organisationDataBlock.classList.add('hidden')
            selectedOrganisation = 'None'
            organisationNameInput.value = selectedOrganisation
        }*/
}
function backFromOrganisations() {
    if (organisationList == null || organisationNameInput == null || organisationDataBlock == null)
        return;
    if (checkbox != null && organisationCheckboxBlock != null) {
        if (checkbox.checked) {
            checkbox.checked = false;
            if (organisationCheckboxBlock.classList.contains('hidden')) {
                organisationCheckboxBlock.classList.remove('hidden');
                console.log('backFromOrganisations if checkbox checked stopBodyScroll');
                stopBodyScroll();
            }
        }
    }
    else {
        console.log('in another dimension');
    }
    console.log('backFromOrganisations if checkbox checked enableBodyScroll');
    enableBodyScroll();
    organisationList.classList.add('hidden');
    selectedOrganisation = 'None';
    organisationNameInput.value = selectedOrganisation;
    organisationDataBlock.classList.add('hidden');
}
function selectOrganisation(orgName, orgUrl) {
    selectedOrganisation = orgName;
    newOrganisationUrl = orgUrl;
}
function submitOrganisation() {
    console.log('are you submitting or whatt');
    if (organisationNameInput == null || organisationDataBlock == null || organisationList == null || organisationUrlInput == null)
        return;
    console.log('submitting');
    organisationNameInput.value = selectedOrganisation;
    organisationNameInput.classList.add('cursor-not-allowed');
    organisationUrlInput.value = newOrganisationUrl;
    organisationDataBlock.classList.remove('hidden');
    console.log('submitOrganisation');
    enableBodyScroll();
    organisationList.classList.add('hidden');
    //Call the function above if it exists.
    if (typeof submitOrganisationChangeForm === "function") {
        organisationNameInput.setAttribute('value', selectedOrganisation);
        organisationUrlInput.setAttribute('value', newOrganisationUrl);
        submitOrganisationChangeForm();
    }
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
    console.log('goBack stopBodyScroll');
    stopBodyScroll();
    uncoverNewOrgTyping(false);
}
