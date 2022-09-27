let selectedOrganisation: string = ''
let newOrganisationUrl: string = ''

const organisationCheckboxBlock = document.getElementById("organisation-starter")

const checkbox = (<HTMLInputElement>document.getElementById("organisation-checkbox"))

const organisationDataBlock: HTMLElement | null = document.getElementById("organisation-data")
const organisationList: HTMLElement | null = document.getElementById("organisation-list")

const organisationNameInput = (<HTMLInputElement>document.getElementById("organisation_name"))
const organisationUrlInput = (<HTMLInputElement>document.getElementById("organisation_url"))


function toggleOrganisationsAdd() {
    if (checkbox == null || organisationDataBlock == null || selectedOrganisation == null || organisationList == null) return

    if (checkbox.checked) {
        organisationList.classList.remove('hidden')
    } else {
        organisationList.classList.add('hidden')
        organisationDataBlock.classList.add('hidden')
        selectedOrganisation = 'None'
        organisationNameInput.value = selectedOrganisation
    }
}


function toggleOrganisationsChange() {
    console.log('neeein')
    if (organisationDataBlock == null || selectedOrganisation == null || organisationList == null) return
    organisationList.classList.remove('hidden')
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
            }
        }

    } else {
        console.log('in another dimension')

    }
    organisationList.classList.add('hidden')
    selectedOrganisation = 'None'
    organisationNameInput.value = selectedOrganisation
    organisationDataBlock.classList.add('hidden')


}


function selectOrganisation(orgName: string, orgUrl: string) {
    selectedOrganisation = orgName
    newOrganisationUrl = orgUrl
}

function submitOrganisation() {


    if (organisationNameInput == null || organisationDataBlock == null || organisationList == null || organisationUrlInput == null) return

    organisationNameInput.value = selectedOrganisation
    organisationNameInput.classList.add('cursor-not-allowed')

    organisationUrlInput.value = newOrganisationUrl

    organisationDataBlock.classList.remove('hidden')

    organisationList.classList.add('hidden')

}

function openAddName() {

    if (organisationNameInput == null || organisationDataBlock == null || organisationList == null) return

    organisationList.classList.add('hidden')
    uncoverNewOrgTyping(true)

}

function goBack() {

    if (organisationList == null) return

    organisationList.classList.remove('hidden')

    uncoverNewOrgTyping(false)
}


