
const organisationDataEnter = (<HTMLInputElement>document.getElementById("organisation-name-enter"))


function uncoverNewOrgTyping(){
    if (organisationDataEnter == null) return

    organisationDataEnter.classList.remove('hidden')
}

//TODO: ADD URL TOO

function addName() {
    const newOrg = document.getElementById("organisation-name").value

    selectOrganisation(newOrg)
    submitOrganisation()


    const organisationDataEnter = document.getElementById("organisation-name-enter")
    organisationDataEnter.classList.add('hidden')

}
