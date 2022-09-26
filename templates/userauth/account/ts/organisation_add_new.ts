const organisationDataEnter: HTMLElement | null = document.getElementById("organisation-name-enter")


function uncoverNewOrgTyping(toOpenInput: boolean) {
    if (organisationDataEnter == null || organisationList == null) return

    if (toOpenInput) {
        organisationDataEnter.classList.remove('hidden')
    } else {
        organisationDataEnter.classList.add('hidden')

    }

}


function addName() {
    if (organisationDataEnter == null) return

    const tempOrgNameInput = (<HTMLInputElement>document.getElementById("organisation-name"))
    const tempOrgUrlInput = (<HTMLInputElement>document.getElementById("organisation-url"))

    if (tempOrgNameInput == null || tempOrgUrlInput == null) return

    if (tempOrgNameInput.value.length < 1) {
        tempOrgNameInput.setAttribute("required", "");
        return
    }

    const newOrgName = tempOrgNameInput.value
    const newOrgUrl = tempOrgUrlInput.value


    selectOrganisation(newOrgName, newOrgUrl)
    submitOrganisation()


    organisationDataEnter.classList.add('hidden')

}
