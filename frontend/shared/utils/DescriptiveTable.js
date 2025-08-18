import $ from "$";
import h from "shared/utils/helpers";

// Method for creating a table for descriptive information
class DescriptiveTable {
    constructor() {
        this._tbl = $('<table class="table table-sm table-striped">');
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
            if (parseFloat(value, 10) === value) value = h.ff(value);
            if (opts.calculated) {
                value = `[${value}]`; // [] = estimated
            }
            var td = $("<td>").html(value);
            if (opts.annotate) {
                td.append("<br>", $('<span class="text-muted">').text(opts.annotate));
            }
            if (opts.pre) {
                td.css("white-space", "pre-wrap");
            }
            this._tbody.append($("<tr>").append($("<th>").html(description)).append(td));
        }
        return this;
    }

    add_tbody_tr_list(description, list_items) {
        if (list_items.length > 0) {
            var ul = $('<ul class="list-group list-group-flush">').append(
                    list_items.map(function (v) {
                        return $('<li class="list-group-item p-0 bg-transparent">').html(v);
                    })
                ),
                tr = $("<tr>").append(`<th>${description}</th>`).append($("<td>").append(ul));

            this._tbody.append(tr);
        }
        return this;
    }

    add_tbody_tr_badge(description, items) {
        if (items.length > 0) {
            const badges = items.map(
                    item => `<a href="${item.url}" class="badge badge-info mr-1">${item.text}</a>`
                ),
                tr = $("<tr>").append(`<th>${description}</th>`).append($("<td>").append(badges));

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
