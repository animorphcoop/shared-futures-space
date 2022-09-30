const orgButton: HTMLElement | null = document.getElementById("organisation-button")


function submitOrganisationChangeForm() {
    if (orgButton == null) return
    orgButton.click()
}

