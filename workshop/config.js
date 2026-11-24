// URL of the Google Apps Script web app that stores the submissions (ends in /exec).
// Deploy steps: educare/git_code_educare/workshop_form/README.md
// If this is empty the form shows "not active yet" and sends nothing.
window.WORKSHOP_ENDPOINT = "https://script.google.com/macros/s/AKfycbydtiCvq-MdcUcUZFFSjeFA2ZEPGXHIsiSPmm6OS1LwPWfTDd2W-TWiI9TgDfPTcDfLUg/exec";

// Submissions close at the end of 31 January 2027, anywhere on Earth (UTC-12).
// The Apps Script enforces the same limit; this one only hides the form.
window.WORKSHOP_CLOSES = "2027-02-01T12:00:00Z";
