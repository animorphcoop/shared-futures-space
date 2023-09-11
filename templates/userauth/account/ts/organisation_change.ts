import { expose } from "@/templates/ts/utils.ts"

const orgButton: HTMLElement | null = document.getElementById("organisation-button")


export function submitOrganisationChangeForm() {
    if (orgButton == null) return
    orgButton.click()
}

expose({ submitOrganisationChangeForm })