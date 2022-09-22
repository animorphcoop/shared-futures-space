let selectedOrganisation: string = ''
const organisationCheckboxBlock = document.getElementById("organisation-starter")

const checkbox = (<HTMLInputElement>document.getElementById("organisation-checkbox"))

const organisationDataBlock: HTMLElement | null = document.getElementById("organisation-data")
const organisationList: HTMLElement | null = document.getElementById("organisation-list")

const organisationInput = (<HTMLInputElement>document.getElementById("organisation"))


//TODO: SET UP ADDING URL TO NEW ORG

function toggleOrganisations() {
    if (checkbox == null || organisationDataBlock == null || selectedOrganisation == null || organisationList == null) return

    if (checkbox.checked) {
        organisationList.classList.remove('hidden')
        organisationDataBlock.classList.remove('hidden')
    } else {
        organisationList.classList.add('hidden')
        organisationDataBlock.classList.add('hidden')
        selectedOrganisation = 'None'
        organisationInput.value = selectedOrganisation
    }
}

function backFromOrganisations() {
    if (organisationList == null || checkbox == null || organisationInput == null || organisationDataBlock == null || organisationCheckboxBlock == null) return


    if (checkbox.checked) {
        organisationList.classList.add('hidden')
        checkbox.checked = false
        selectedOrganisation = 'None'
        organisationInput.value = selectedOrganisation
        organisationDataBlock.classList.add('hidden')
        if (organisationCheckboxBlock.classList.contains('hidden')) {
            organisationCheckboxBlock.classList.remove('hidden')
        }
    }

}


function selectOrganisation(orgName: string) {
    selectedOrganisation = orgName
}

function submitOrganisation() {
    console.log(`Selected ${selectedOrganisation}`)


    if (organisationInput == null || organisationDataBlock == null || organisationList == null) return

    organisationInput.value = selectedOrganisation
    organisationInput.classList.add('cursor-not-allowed')

    organisationDataBlock.classList.remove('hidden')

    organisationList.classList.add('hidden')

}

function openAddName() {

    if (organisationInput == null || organisationDataBlock == null || organisationList == null) return

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
