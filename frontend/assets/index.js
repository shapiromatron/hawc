// startup
import "utils/startup";

// custom applications
import nestedTagEditorStartup from "nestedTagEditor";
import smartTagsStartup from "smartTags/split";
import textCleanupStartup from "textCleanup";

window.app.nestedTagEditorStartup = nestedTagEditorStartup;
window.app.smartTagsStartup = smartTagsStartup;
window.app.textCleanupStartup = textCleanupStartup;

export default {
    nestedTagEditorStartup,
    smartTagsStartup,
    textCleanupStartup,
};
