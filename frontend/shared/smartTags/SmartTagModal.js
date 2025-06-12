import Endpoint from "animal/Endpoint";
import Study from "study/Study";
import DataPivot from "summary/dataPivot/DataPivot";
import Visual from "summary/summary/Visual";
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

    renderModal(_e) {
        if (!this.isActive) {
            return;
        }
        let Cls = this.getModelClass(this.type);
        if (Cls) {
            Cls.displayAsModal(this.pk);
        }
    }

    getModelClass(_type) {
        let map = {
            endpoint: Endpoint,
            study: Study,
            visual: Visual,
            data_pivot: DataPivot,
        };
        return map[this.type];
    }
}

export default SmartTagModal;
