export default function tryWebAppStartup() {
    /*
    Attempts to start webpack application startup if current page has requirements.

    If both a #config and #main are present, parse #config as JSON and then start selected
    application, inserting content into the #main element.

    If requirements are not present, noop.
     */
    const el = document.getElementById("main"),
        config = document.getElementById("config");
    if (el && config) {
        const content = JSON.parse(config.textContent);
        window.app.startup(content.app, app => {
            const func = content.page ? app[content.page] : app;
            func(el, content.data);
        });
    }
}
