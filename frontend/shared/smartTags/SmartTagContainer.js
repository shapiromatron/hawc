import $ from "$";

import SmartTagModal from "./SmartTagModal";

class SmartTagContainer {
    constructor($el, options) {
        this.options = options || {};
        this.$el = $el;
        if (this.options.showOnStartup) {
            this.renderAndEnable();
        }
    }

    renderAndEnable() {
        this.enableModals();
    }

    unrenderAndDisable() {
        this.disableModals();
    }

    enableModals() {
        this.$el.find("span.smart-tag").each(function() {
            let st = $(this).data("_smartTag");
            if (!st) {
                st = new SmartTagModal(this);
            }
            st.enable();
        });
    }

    disableModals() {
        this.$el.find("span.smart-tag").each(function() {
            let st = $(this).data("_smartTag");
            if (!st) {
                st = new SmartTagModal(this);
            }
            st.disable();
        });
    }
}

export default SmartTagContainer;
