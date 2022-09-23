let selectedOrganisation: string = ''
let newOrganisationUrl: string = ''

const organisationCheckboxBlock = document.getElementById("organisation-starter")

const checkbox = (<HTMLInputElement>document.getElementById("organisation-checkbox"))

const organisationDataBlock: HTMLElement | null = document.getElementById("organisation-data")
const organisationList: HTMLElement | null = document.getElementById("organisation-list")

const organisationNameInput = (<HTMLInputElement>document.getElementById("organisation_name"))
const organisationUrlInput = (<HTMLInputElement>document.getElementById("organisation_url"))


function toggleOrganisations() {
    if (checkbox == null || organisationDataBlock == null || selectedOrganisation == null || organisationList == null) return

    if (checkbox.checked) {
        organisationList.classList.remove('hidden')
        //organisationDataBlock.classList.remove('hidden')
    } else {
        organisationList.classList.add('hidden')
        organisationDataBlock.classList.add('hidden')
        selectedOrganisation = 'None'
        organisationNameInput.value = selectedOrganisation
    }
}

function backFromOrganisations() {
    if (organisationList == null || checkbox == null || organisationNameInput == null || organisationDataBlock == null || organisationCheckboxBlock == null) return


    if (checkbox.checked) {
        organisationList.classList.add('hidden')
        checkbox.checked = false
        selectedOrganisation = 'None'
        organisationNameInput.value = selectedOrganisation
        organisationDataBlock.classList.add('hidden')
        if (organisationCheckboxBlock.classList.contains('hidden')) {
            organisationCheckboxBlock.classList.remove('hidden')
        }
    }

}


function selectOrganisation(orgName: string, orgUrl: string) {
    selectedOrganisation = orgName
    newOrganisationUrl = orgUrl
}

function submitOrganisation() {
    console.log(`Selected ${selectedOrganisation}`)


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
    uncoverNewOrgTyping()

}

/*

function addName() {
    const newOrg = document.getElementById("organisation-name").value

    selectOrganisation(newOrg)
    submitOrganisation()


    const organisationDataEnter = document.getElementById("organisation-name-enter")
    organisationDataEnter.classList.add('hidden')

}
*/
