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
    const tempOrgNameInput = document.getElementById("organisation-name-temp");
    const errorBoxUrl = document.getElementById("error-box-url");
    const tempOrgUrlInput = document.getElementById("organisation-url-temp");
    if (tempOrgNameInput == null || tempOrgUrlInput == null || errorBoxName == null || errorBoxUrl == null)
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
    /* basic url validation*/
    let urlString = tempOrgUrlInput.value;
    /*if the url field is empty then we are happy to process it as such, otherwise validate*/
    if (urlString.length > 1) {
        /*url has to have at least one dot*/
        // @ts-ignore
        if (!urlString.includes(".") || !urlString.includes("https://")) {
            if (errorBoxUrl.classList.contains('hidden')) {
                errorBoxUrl.classList.remove('hidden');
            }
            return;
        }
        /*url has to have something before and after the dot, not worried about the details*/
        /*TODO: Extend and consolidate validation*/
        let urlArray = urlString.split(".");
        console.log(urlArray.length);
        if (urlArray.length < 2 || urlArray[0] == "" || urlArray[1] == "") {
            if (errorBoxUrl.classList.contains('hidden')) {
                errorBoxUrl.classList.remove('hidden');
            }
            return;
        }
    }
    if (!errorBoxUrl.classList.contains('hidden')) {
        errorBoxUrl.classList.add('hidden');
    }
    const newOrgName = tempOrgNameInput.value;
    const newOrgUrl = tempOrgUrlInput.value;
    selectOrganisation(newOrgName, newOrgUrl);
    submitOrganisation();
    organisationDataEnter.classList.add('hidden');
}
