export default function tryWebAppStartup() {
    /* This method runs on each page in HAWC. It checks if a #config div is present, and if so,
     * parses the configuration and attempts to start the selected javascript frontend application.
     */
    const el = document.getElementById("main"),
        config = document.getElementById("config");
    if (el && config) {
        const content = JSON.parse(config.textContent);
        window.app.startup(content.app, function(app) {
            if (content.page) {
                app[content.page](el, content.data);
            } else {
                app(el, content.data);
            }
        });
    }
}
