// startup
import 'utils/startup';

// custom applications
import nestedTagEditorStartup from 'nestedTagEditor';
import smartTagsStartup from 'smartTags/split';
import textCleanupStartup from 'textCleanup';

window.app = {
    nestedTagEditorStartup,
    smartTagsStartup,
    textCleanupStartup,
};
