import $ from "$";

// Method for creating a table for descriptive information
class DescriptiveTable {
    constructor() {
        this._tbl = $('<table class="table table-condensed table-striped">');
        this._colgroup = $("<colgroup>").append(
            '<col style="width: 30%;"><col style="width: 70%;">'
        );
        this._tbody = $("<tbody>");
        this._tbl.append(this._colgroup, this._tbody);
        return this;
    }

    add_tbody_tr(description, value, opts) {
        opts = opts || {};
        if (value) {
            if (parseFloat(value, 10) === value) value = value.toHawcString();
            if (opts.calculated) {
                value = `[${value}]`; // [] = estimated
            }
            var td = $("<td>").html(value);
            if (opts.annotate) {
                td.append("<br>", $('<span class="muted">').text(opts.annotate));
            }
            this._tbody.append(
                $("<tr>")
                    .append($("<th>").html(description))
                    .append(td)
            );
        }
        return this;
    }

    add_tbody_tr_list(description, list_items) {
        if (list_items.length > 0) {
            var ul = $("<ul>").append(
                    list_items.map(function(v) {
                        return $("<li>").html(v);
                    })
                ),
                tr = $("<tr>")
                    .append(`<th>${description}</th>`)
                    .append($("<td>").append(ul));

            this._tbody.append(tr);
        }
        return this;
    }

    get_tbl() {
        return this._tbl;
    }

    get_tbody() {
        return this._tbody;
    }
}

export default DescriptiveTable;
