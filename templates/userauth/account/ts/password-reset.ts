/*only if the email input field is 5+ chars we send request to django to check if it's valid.*/
function emailLength(textInput: string) {
    return textInput.length >= 5
}
