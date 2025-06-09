import $ from "$";

import SmartTagInline from "./SmartTagInline";
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
        this.renderInlines();
        this.enableModals();
    }

    unrenderAndDisable() {
        this.unrenderInlines();
        this.disableModals();
    }

    renderInlines() {
        this.$el.find("div.smart-tag").each(function () {
            let st = $(this).data("_smartTag");
            if (!st) {
                st = new SmartTagInline(this);
            }
            st.render();
        });
    }

    unrenderInlines(_$el) {
        this.$el.find("div.smart-tag").each(function () {
            let st = $(this).data("_smartTag");
            if (!st) {
                st = new SmartTagInline(this);
            }
            st.unrender();
        });
    }

    enableModals() {
        this.$el.find("span.smart-tag").each(function () {
            let st = $(this).data("_smartTag");
            if (!st) {
                st = new SmartTagModal(this);
            }
            st.enable();
        });
    }

    disableModals() {
        this.$el.find("span.smart-tag").each(function () {
            let st = $(this).data("_smartTag");
            if (!st) {
                st = new SmartTagModal(this);
            }
            st.disable();
        });
    }
}

export default SmartTagContainer;
