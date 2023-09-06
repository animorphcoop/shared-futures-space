import {expose} from "@/templates/ts/utils.ts";
import { submitOrganisationChangeForm } from "@/templates/userauth/account/ts/organisation_change.ts"
import { uncoverNewOrgTyping } from "@/templates/userauth/account/ts/organisation_add_new.ts"

let selectedOrganisation: string = ''
let newOrganisationUrl: string = ''
//if (organisationNameInput == null || organisationDataBlock == null || organisationList == null || organisationUrlInput == null) return

const organisationCheckboxBlock = document.getElementById("organisation-starter")

const checkbox = (<HTMLInputElement>document.getElementById("organisation-checkbox"))

const organisationDataBlock: HTMLElement | null = document.getElementById("organisation-data")
export const organisationList: HTMLElement | null = document.getElementById("organisation-list")

const organisationNameInput = (<HTMLInputElement>document.getElementById("organisation-name"))
const organisationUrlInput = (<HTMLInputElement>document.getElementById("organisation-url"))

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
}
window.addEventListener('scroll', () => {
    document.documentElement.style.setProperty('--scroll-y', `${window.scrollY}px`);
});

function toggleOrganisationsAdd() {
    if (checkbox == null || organisationDataBlock == null || selectedOrganisation == null || organisationList == null) return

    if (checkbox.checked) {
        organisationList.classList.remove('hidden')
        stopBodyScroll();
    } else {

        organisationList.classList.add('hidden')
        organisationDataBlock.classList.add('hidden')
        selectedOrganisation = 'None'
        organisationNameInput.value = selectedOrganisation
    }
}

function toggleOrganisationsChange() {
    if (organisationDataBlock == null || selectedOrganisation == null || organisationList == null) return
    organisationDataBlock.classList.remove('hidden')

    organisationList.classList.remove('hidden')
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
    if (organisationList == null || organisationNameInput == null || organisationDataBlock == null) return
    if (checkbox != null && organisationCheckboxBlock != null) {

        if (checkbox.checked) {

            checkbox.checked = false

            if (organisationCheckboxBlock.classList.contains('hidden')) {
                organisationCheckboxBlock.classList.remove('hidden')
                stopBodyScroll();
            }
        }

    }
    enableBodyScroll();
    organisationList.classList.add('hidden')
    selectedOrganisation = 'None'
    organisationNameInput.value = selectedOrganisation
    organisationDataBlock.classList.add('hidden')
}

/*
* when called from the list of organisations orgUrl will be undefined,
* the url is only needed when creating a new organisation in CustomAddDataView
* */
export function selectOrganisation(orgName: string, orgUrl: string) {
    selectedOrganisation = orgName
    if (typeof orgUrl !== "undefined") {
        newOrganisationUrl = orgUrl
    }
}

export function submitOrganisation() {

    if (organisationNameInput == null || organisationDataBlock == null || organisationList == null || organisationUrlInput == null) return

    //if (organisationNameInput.value == "") return
    if (selectedOrganisation == "") return

    organisationNameInput.value = selectedOrganisation
    organisationNameInput.classList.add('cursor-not-allowed')
    if (newOrganisationUrl != '') {
        organisationUrlInput.value = newOrganisationUrl
    }

    organisationDataBlock.classList.remove('hidden')

    enableBodyScroll();
    organisationList.classList.add('hidden')

    //Call the function above if it exists.
    if (typeof submitOrganisationChangeForm === "function") {
        organisationNameInput.setAttribute('value', selectedOrganisation)
        organisationUrlInput.setAttribute('value', newOrganisationUrl)

        submitOrganisationChangeForm();
    }

}

function openAddName() {

    if (organisationNameInput == null || organisationDataBlock == null || organisationList == null) return

    organisationList.classList.add('hidden')
    uncoverNewOrgTyping(true)

}

function goBack() {

    if (organisationList == null) return

    organisationList.classList.remove('hidden')
    stopBodyScroll();

    uncoverNewOrgTyping(false)
}

expose({
    stopBodyScroll,
    enableBodyScroll,
    toggleOrganisationsAdd,
    toggleOrganisationsChange,
    backFromOrganisations,
    selectOrganisation,
    submitOrganisation,
    openAddName,
    goBack,
})

