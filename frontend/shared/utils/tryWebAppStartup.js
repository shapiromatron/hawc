export default function tryWebAppStartup() {
    /*
    Attempts to start JS startup if current page has requirements.

    If both a #config and #main are present, parse #config as JSON and then start selected
    application, inserting content into the #main element.

    If requirements are not present, noop.
     */
    const config = document.getElementById("config"),
        content = config ? JSON.parse(config.textContent) : {},
        el = content.selector
            ? document.querySelector(content.selector)
            : document.getElementById("main");
    if (el && config) {
        window.app.startup(content.app, app => {
            const func = content.page ? app[content.page] : app;
            func(el, content.data);
        });
    }
}
