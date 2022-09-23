
const organisationDataEnter = (<HTMLInputElement>document.getElementById("organisation-name-enter"))


function uncoverNewOrgTyping(){
    if (organisationDataEnter == null) return

    organisationDataEnter.classList.remove('hidden')
}

//TODO: ADD URL TOO

function addName() {
    const newOrgName = document.getElementById("organisation-name").value
    const newOrgUrl = document.getElementById("organisation-url").value

    selectOrganisation(newOrgName, newOrgUrl)
    submitOrganisation()


    const organisationDataEnter = document.getElementById("organisation-name-enter")
    organisationDataEnter.classList.add('hidden')

}
