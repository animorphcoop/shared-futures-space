"use strict";
/* Needs auth-helper to run */
// triggered from x-init on the form
function setupObserversWizard() {
    if (submitButton.classList.contains('cursor-not-allowed')) {
        submitButton.classList.remove('cursor-not-allowed');
        submitButton.disabled = false;
    }
}
