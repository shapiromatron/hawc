import _ from "lodash";

import $ from "$";

class DoseUnitsWidget {
    constructor(form, opts) {
        // DoseUnitsWidget not shown for file data pivot
        if ($(opts.el).length === 0) {
            return;
        }

        form.on("submit", this.handleFormSubmit.bind(this));
        this.$input = $(opts.el).hide();
        this.$widgetDiv = $("#pduDiv");
        this.$available = $("#pduAvailable");
        this.$selected = $("#pduSelected");
        $("#pduAdd").on("click", this.handleAdd.bind(this));
        $("#pduRemove").on("click", this.handleRemove.bind(this));
        $("#pduUp").on("click", this.handleUp.bind(this));
        $("#pduDown").on("click", this.handleDown.bind(this));
        this.render(opts.choices);
    }

    handleAdd() {
        // add new units, after de-duping those already available.
        var optsMap = {};
        this.$available.find("option:selected").each(function (i, el) {
            optsMap[el.value] = el;
        });
        this.$selected.find("option").each(function (i, el) {
            delete optsMap[el.value];
        });
        this.$selected.append($(_.values(optsMap)).clone());
    }

    handleRemove() {
        this.$selected.find("option:selected").remove();
    }

    handleUp() {
        this.$selected.find("option:selected").each(function (i, el) {
            var $el = $(el);
            $el.insertBefore($el.prev());
        });
    }

    handleDown() {
        this.$selected
            .find("option:selected")
            .get()
            .reverse()
            .forEach(function (el) {
                var $el = $(el);
                $el.insertAfter($el.next());
            });
    }

    handleFormSubmit() {
        var selected_ids = this.$selected
            .children()
            .map(function (i, el) {
                return parseInt(el.value);
            })
            .get();
        this.$input.val(selected_ids.join(","));
        return true;
    }

    render(objects) {
        var self = this;

        // set available
        objects.forEach(function (d) {
            self.$available.append(`<option value="${d.id}">${d.name}</option>`);
        });

        //set selected
        var objectsKeymap = _.keyBy(objects, "id"),
            ids = this.$input
                .val()
                .split(",")
                .filter(d => d.length > 0)
                .map(d => parseInt(d));

        ids.forEach(function (d) {
            var dose = objectsKeymap[d];
            self.$selected.append(`<option value="${dose.id}">${dose.name}</option>`);
        });

        //render on DOM
        this.$input.parent().prepend(this.$widgetDiv);
        this.$widgetDiv.show();
    }
}

export default DoseUnitsWidget;
