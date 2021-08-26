import $ from "$";

import SmartTagContainer from "./SmartTagContainer";

class SmartTagEditor extends SmartTagContainer {
    constructor($el, options) {
        $el.quillify();
        super(...arguments);
        if (this.options.submitEl) {
            $(options.submitEl).submit(this.prepareSubmission.bind(this));
        }
    }

    prepareSubmission() {
        this.unrenderAndDisable();
        return true;
    }

    setContent(content) {
        let q = this.$el.data("_quill");
        q.pasteHTML(content);
        this.renderAndEnable();
    }
}

export default SmartTagEditor;
