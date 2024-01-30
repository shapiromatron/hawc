document.body.addEventListener('htmx:afterRequest', function (evt) {
    const errorAlert = document.getElementById("htmx-alert")
    const errorBanner = document.getElementById("htmx-error-banner")
    if (evt.detail.successful) {
        // Successful request, clear out alert
        errorBanner.setAttribute("hidden", "true")
        errorAlert.innerText = "";
    } else if (evt.detail.failed && evt.detail.xhr) {
        // Server error with response contents, equivalent to htmx:responseError
        console.warn("Server error", evt.detail)
        const xhr = evt.detail.xhr;
        errorAlert.innerText = `Unexpected server error: ${xhr.status} - ${xhr.statusText}`;
        errorBanner.removeAttribute("hidden");
    } else {
        // Unspecified failure, usually caused by network error
        console.error("Unexpected htmx error", evt.detail)
        errorAlert.innerText = "Unexpected error";
        errorBanner.removeAttribute("hidden");
    }
});
