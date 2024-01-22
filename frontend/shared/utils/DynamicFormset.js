import _ from "lodash";

import $ from "$";

// Dynamic formset to add and remove forms via JS
class DynamicFormset {
    constructor($formset, prefix, options) {
        // Modified from https://djangosnippets.org/snippets/1389/
        this.$el = $formset;
        this.prefix = prefix;
        this.options = options || {oneFormRequired: false};
        this.$el.find(".formset th").tooltip({trigger: "hover"});
        this.$el.on("click", "#addFormToFormset", this.addForm.bind(this));
        this.$el.on("click", ".deleteForm", this.deleteForm.bind(this));
    }

    updateElementIndex(el, idx) {
        var id_regex = new RegExp("(" + this.prefix + "-\\d+)"),
            replacement = this.prefix + "-" + idx;
        if (el.id) el.id = el.id.replace(id_regex, replacement);
        if (el.name) el.name = el.name.replace(id_regex, replacement);
    }

    addForm() {
        // clone row and remove values
        var forms = this._formsInFormset(),
            row = forms.last().clone(false);

        this.clearForm(row);
        row.insertAfter(forms.last());

        // update form index
        this._updateFieldIndices();

        // update form count
        this._updateTotalFormsField();

        // trigger events
        this._formsInFormset().trigger("dynamicFormset-formAdded");
    }

    _updateFieldIndices() {
        var self = this;
        this._formsInFormset().each(function (i, tr) {
            _.each($(tr).find("input,select"), function (inp) {
                self.updateElementIndex(inp, i);
            });
        });
    }

    _formsInFormset() {
        return this.$el.find(".dynamic-form");
    }

    _updateTotalFormsField() {
        $(`#id_${this.prefix}-TOTAL_FORMS`).val(this._formsInFormset().length);
    }

    deleteForm(e) {
        if (this.options.oneFormRequired && this._formsInFormset().length <= 1) {
            return alert("Cannot remove all forms.");
        }

        // remove current form
        $(e.target).parents(".dynamic-form").remove();

        // update form count
        this._updateTotalFormsField();

        // update form index
        this._updateFieldIndices();

        // trigger events
        this._formsInFormset().trigger("dynamicFormset-formRemoved");
    }

    clearForm($row) {
        $row.find("input,select").val("");
        $row.find("select").each((i, sel) => {
            if ($(sel).find("option").length > 0) {
                $(sel).find("option:first").prop("selected", true);
            }
        });
    }
}

export default DynamicFormset;
