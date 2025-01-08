import Study from "study/Study";

import $ from "$";

class SmartTagModal {
    constructor(span) {
        this.$span = $(span);
        this.type = this.$span.data("type");
        this.pk = this.$span.data("pk");
        this.$span.click(this.renderModal.bind(this));
        this.$span.data("_smartTag", this);
    }

    enable() {
        this.isActive = true;
        this.$span.addClass("active");
    }

    disable() {
        this.isActive = false;
        this.$span.removeClass("active");
    }

    renderModal(e) {
        if (!this.isActive) {
            return;
        }
        let Cls = this.getModelClass(this.type);
        if (Cls) {
            Cls.displayAsModal(this.pk);
        }
    }

    getModelClass(type) {
        let map = {study: Study};
        return map[this.type];
    }
}

export default SmartTagModal;
