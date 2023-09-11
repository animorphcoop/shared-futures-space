/* Needs auth-helper to run */

import { expose } from "@/templates/ts/utils.ts"
import { submitButton } from "@/templates/userauth/account/ts/auth_helper.ts"

// triggered from x-init on the form
function setupObserversWizard() {
    if (submitButton.classList.contains('cursor-not-allowed')) {
        submitButton.classList.remove('cursor-not-allowed')
        submitButton.disabled = false
    }
}

expose({ setupObserversWizard })
