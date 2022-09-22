let selectedOrganisation = ''


function toggleOrganisations() {
    const organisationList = document.getElementById("organisation-list")
    const checkbox = document.getElementById("organisation-checkbox")
    const organisationData = document.getElementById("organisation-data")
    const organisationInput = document.getElementById("organisation")

    if (checkbox.checked) {
        organisationList.classList.remove('hidden')
        organisationData.classList.remove('hidden')
    } else {
        organisationList.classList.add('hidden')
        organisationData.classList.add('hidden')
        selectedOrganisation = 'None'
        organisationInput.value = selectedOrganisation
    }
}

function backFromOrganisations() {
    const organisationList = document.getElementById("organisation-list")
    const checkbox = document.getElementById("organisation-checkbox")
    const organisationData = document.getElementById("organisation-data")
    const organisationInputBox = document.getElementById("organisation-starter")
    //organisationInputBox.classList.add('hidden')

    if (checkbox.checked) {
        organisationList.classList.add('hidden')
        checkbox.checked = false
        const organisationInput = document.getElementById("organisation")
        selectedOrganisation = 'None'
        organisationInput.value = selectedOrganisation
        organisationData.classList.add('hidden')
        if (organisationInputBox.classList.contains('hidden')) {
            organisationInputBox.classList.remove('hidden')
        }
    }

}


function selectOrganisation(orgName) {
    selectedOrganisation = orgName
}

function submitOrganisation() {
    console.log(`Selected ${selectedOrganisation}`)

    const organisationInput = document.getElementById("organisation")
    organisationInput.value = selectedOrganisation
    organisationInput.classList.add('cursor-not-allowed')

    const organisationDataBlock = document.getElementById("organisation-data")
    organisationDataBlock.classList.remove('hidden')

    const organisationList = document.getElementById("organisation-list")
    organisationList.classList.add('hidden')

}

function openAddName() {

    const organisationList = document.getElementById("organisation-list")
    organisationList.classList.add('hidden')
    const organisationDataEnter = document.getElementById("organisation-name-enter")
    organisationDataEnter.classList.remove('hidden')
}

function addName() {
    const newOrg = document.getElementById("organisation-name").value

    selectOrganisation(newOrg)
    submitOrganisation()


    const organisationDataEnter = document.getElementById("organisation-name-enter")
    organisationDataEnter.classList.add('hidden')

}
