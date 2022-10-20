"use strict";
/* Needs auth-helper to run - same as login - will be merged when TS files speak to each other*/
// triggered from x-init on the form
function setupObserversReset() {
    if (inputFeedback == null)
        return;
    newObserver(emailInput, inputFeedback, () => { });
    toggleSubmitButton(true);
}
function validateReset() {
    if (inputFeedback === null)
        return;
    let errorCount = 0;
    errorCount += validateInputFeedback(emailInput, inputFeedback);
    return errorCount == 0;
}
