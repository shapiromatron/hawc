import _ from "lodash";

import $ from "$";

class SmartTagModal {
    constructor(quill, modal) {
        this.quill = quill;
        this.modal = modal;
        this.setupEventListeners();
    }

    setupEventListeners() {
        let m = this.modal;

        m.find("#id_resource")
            .off("change")
            .change(function() {
                let v = $(this).val(),
                    show,
                    hides = ["#div_id_study"];
                if (v === "study") {
                    show = hides.splice(hides.indexOf("#div_id_study"), 1);
                }
                m.find(show.join(",")).show();
                m.find(hides.join(",")).hide();
            })
            .trigger("change");

        m.find(".smartTagSave")
            .off("click")
            .click(this.tryToSave.bind(this));

        m.on("shown.bs.modal", () => m.find("input").val(""));

        m.on("shown.bs.modal", () => {
            this.quill.blur();
            m.find("input:visible").focus();
        });

        m.on("hidden.bs.modal", () => this.quill.stc.enableModals());
    }

    setInitialValues() {}

    getDefaultValues() {
        return {
            type: "study",
            id: null,
        };
    }

    showModal(type, selection, values) {
        this.type = type;
        this.selection = selection;
        if (values === undefined) {
            values = this.getDefaultValues();
        }
        this.setInitialValues();
        this.modal.modal("show");
    }

    getFormValues() {
        let m = this.modal,
            type = m.find("#id_resource").val(),
            pk;

        switch (type) {
            case "study":
                pk = m.find("#id_study").val();
                break;
        }

        pk = parseInt(pk);
        if (_.isNaN(pk)) {
            return null;
        } else {
            return {type, pk};
        }
    }

    tryToSave() {
        let values = this.getFormValues();
        if (values) {
            this.quill.setSelection(this.selection);
            this.quill.format(this.type, values);
        }
        this.modal.modal("hide");
    }
}

export default SmartTagModal;
