var supportedBrowserCheck = function() {
    /*
    Add a warning to the application if an unsupported browser is used. Currently supported
    browsers are chrome, safari, or firefox. Edge appears to work but we don't officially support.
    IE11 is unsupported.

    Tested using github gist:
        https://gist.github.com/shapiromatron/bae66a34e30c8d6c518676f39592fed4

    Validated that the error is shown on IE11 but not on the chrome, firefox, safari, or edge.
    */
    var isSupportedBrowser = function () {
        // not ideal; but <IE12 isn't supported which is primary-goal:
        // http://webaim.org/blog/user-agent-string-history/
        var ua = navigator.userAgent.toLowerCase(),
            isChrome = ua.indexOf("chrome") > -1,
            isFirefox = ua.indexOf("firefox") > -1,
            isSafari = ua.indexOf("safari") > -1;
        return isChrome || isFirefox || isSafari;
    }

    if (!isSupportedBrowser()) {
        $("#main-content-container").prepend(
            '<div class="alert">\
                <p><b>Warning:</b> Your current browser has not been tested extensively with this website, which may result in some some errors with functionality. The following browsers are fully supported:</p>\
                <ul>\
                    <li><a href="https://www.google.com/chrome/" target="_blank">Google Chrome</a> (preferred)</li>\
                    <li><a href="https://www.mozilla.org/firefox/" target="_blank">Mozilla Firefox</a></li>\
                    <li><a href="https://www.apple.com/safari/" target="_blank">Apple Safari</a></li>\
                </ul>\
                <p>Please use a different browser for an optimal experience.</p>\
            </div>'
        );
    }
}
