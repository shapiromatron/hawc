import _ from "lodash";
import HAWCUtils from "shared/utils/HAWCUtils";
import D3Visualization from "summary/summary/D3Visualization";

import $ from "$";

import {HeaderNullField, HelpTextNullField, InputField, SpacerNullField} from "./Fields";

class TableField extends InputField {
    renderHeader() {
        return HAWCUtils.abstractMethod();
    }

    addRow() {
        return HAWCUtils.abstractMethod();
    }

    fromSerializedRow() {
        return HAWCUtils.abstractMethod();
    }

    toSerializedRow() {
        return HAWCUtils.abstractMethod();
    }

    toSerialized() {
        this.parent.settings[this.schema.name] = _.chain(this.$tbody.children())
            .map(_.bind(this.toSerializedRow, this))
            .compact()
            .value();
    }

    fromSerialized() {
        var arr = this.parent.settings[this.schema.name] || [];
        this.$tbody.empty();
        if (arr.length === 0 && this.schema.addBlankRowIfNone) {
            this.addRow();
        } else {
            _.each(arr, _.bind(this.fromSerializedRow, this));
        }
    }

    setColgroup() {
        var cw = this.schema.colWidths || [],
            setCol = d => `<col width="${d}%"`;
        $("<colgroup>").append(_.map(cw, setCol)).appendTo(this.table);
    }

    render() {
        var $div = $('<div class="form-group form-row">');

        if (this.schema.prependSpacer) new SpacerNullField(this.schema, this.$parent).render();
        if (this.schema.label) new HeaderNullField(this.schema, this.$parent).render();
        if (this.schema.helpText) new HelpTextNullField(this.schema, this.$parent).render();

        this.table = $('<table class="table table-sm table-bordered">').appendTo($div);
        this.setColgroup();
        this.$thead = $("<thead>").appendTo(this.table);
        this.$tbody = $("<tbody>").appendTo(this.table);
        this.renderHeader();
        $div.appendTo(this.$parent);
    }

    thOrdering(options) {
        var th = $("<th>").html("Ordering&nbsp;"),
            add = $(
                '<button class="btn btn-sm btn-primary float-right" title="Add row"><i class="fa fa-plus"></button>'
            ).on("click", this.addRow.bind(this));

        if (options.showNew) th.append(add);
        return th;
    }

    tdOrdering() {
        var moveUp = function () {
                var tr = $(this.parentNode.parentNode),
                    prev = tr.prev();
                if (prev.length > 0) tr.insertBefore(prev);
            },
            moveDown = function () {
                var tr = $(this.parentNode.parentNode),
                    next = tr.next();
                if (next.length > 0) tr.insertAfter(next);
            },
            del = function () {
                $(this.parentNode.parentNode).remove();
            },
            td = $("<td class='float-right'>");

        td.append(
            $(
                '<button class="btn btn-sm btn-info" title="Move up"><i class="fa fa-arrow-up"></button>'
            ).on("click", moveUp),
            $(
                '<button class="btn btn-sm btn-info mx-1" title="Move down"><i class="fa fa-arrow-down"></button>'
            ).on("click", moveDown),
            $(
                '<button class="btn btn-sm btn-danger" title="Remove"><i class="fa fa-trash"></button>'
            ).on("click", del)
        );
        return td;
    }

    addTdP(cls, txt) {
        return $("<td>").append($("<p>").attr("class", cls).text(txt));
    }

    addTdText(name, val) {
        val = val || "";
        return $(`<td><input name="${name}" value="${val}" class="form-control" type="text"></td>`);
    }

    addTdInt(name, val) {
        val = val || "";
        return `<td><input name="${name}" value="${val}" class="form-control" type="number"></td>`;
    }

    addTdFloat(name, val) {
        val = val || "";
        return `<td><input name="${name}" value="${val}" class="form-control" type="number" step="any"></td>`;
    }

    addTdColor(name, val) {
        val = val || "#000000";
        return $("<td>").append(
            $(`<input type="color" name="${name}" value="${val}" class="form-control" required>`)
        );
    }

    addTdCheckbox(name, checked) {
        let checkProp = checked ? "checked" : "";
        return $("<td>").append(`<div class="form-check">
            <input type="checkbox" name="${name}" ${checkProp} required>
        </div>`);
    }

    addTdSelect(name, values) {
        var sel = $(`<select name="${name}" class="form-control">`).append(
            _.map(values, d => `<option value="${d}">${d}</option>`)
        );
        return $("<td>").append(sel);
    }

    addTdSelectLabels(name, options) {
        var sel = $(`<select name="${name}" class="form-control">`).append(
            _.map(options, d => `<option value="${d.id}">${d.label}</option>`)
        );
        return $("<td>").append(sel);
    }

    addTdSelectMultiple(name, values) {
        var sel = $(`<select name="${name}" class="form-control" multiple>`).append(
            _.map(values, d => `<option value="${d}">${d}</option>`)
        );
        return $("<td>").append(sel);
    }
}

class ReferenceLineField extends TableField {
    renderHeader() {
        return $("<tr>")
            .append(
                "<th>Line value</th>",
                "<th>Caption</th>",
                "<th>Style</th>",
                this.thOrdering({showNew: true})
            )
            .appendTo(this.$thead);
    }

    addRow() {
        return $("<tr>")
            .append(
                this.addTdFloat("value"),
                this.addTdText("title"),
                this.addTdSelect("style", _.map(D3Visualization.styles.lines, "name")),
                this.tdOrdering()
            )
            .appendTo(this.$tbody);
    }

    fromSerializedRow(d, i) {
        var row = this.addRow();
        row.find('input[name="value"]').val(d.value);
        row.find('input[name="title"]').val(d.title);
        row.find('select[name="style"]').val(d.style);
    }

    toSerializedRow(row) {
        row = $(row);
        return {
            value: parseFloat(row.find('input[name="value"]').val(), 10),
            title: row.find('input[name="title"]').val(),
            style: row.find('select[name="style"]').val(),
        };
    }
}

class ReferenceRangeField extends TableField {
    renderHeader() {
        return $("<tr>")
            .append(
                "<th>Lower value</th>",
                "<th>Upper value</th>",
                "<th>Caption</th>",
                "<th>Style</th>",
                this.thOrdering({showNew: true})
            )
            .appendTo(this.$thead);
    }

    addRow() {
        return $("<tr>")
            .append(
                this.addTdFloat("lower"),
                this.addTdFloat("upper"),
                this.addTdText("title"),
                this.addTdSelect("style", _.map(D3Visualization.styles.rectangles, "name")),
                this.tdOrdering()
            )
            .appendTo(this.$tbody);
    }

    fromSerializedRow(d, i) {
        var row = this.addRow();
        row.find('input[name="lower"]').val(d.lower);
        row.find('input[name="upper"]').val(d.upper);
        row.find('input[name="title"]').val(d.title);
        row.find('select[name="style"]').val(d.style);
    }

    toSerializedRow(row) {
        row = $(row);
        return {
            lower: parseFloat(row.find('input[name="lower"]').val(), 10),
            upper: parseFloat(row.find('input[name="upper"]').val(), 10),
            title: row.find('input[name="title"]').val(),
            style: row.find('select[name="style"]').val(),
        };
    }
}

class ReferenceLabelField extends TableField {
    renderHeader() {
        return $("<tr>")
            .append(
                "<th>Caption</th>",
                "<th>Style</th>",
                "<th>Max width (px)</th>",
                "<th>X position</th>",
                "<th>Y position</th>",
                this.thOrdering({showNew: true})
            )
            .appendTo(this.$thead);
    }

    addRow() {
        return $("<tr>")
            .append(
                this.addTdText("caption"),
                this.addTdSelect("style", _.map(D3Visualization.styles.texts, "name")),
                this.addTdInt("max_width", 0),
                this.addTdInt("x", 0),
                this.addTdInt("y", 0),
                this.tdOrdering()
            )
            .appendTo(this.$tbody);
    }

    fromSerializedRow(d, i) {
        var row = this.addRow();
        row.find('input[name="caption"]').val(d.caption);
        row.find('select[name="style"]').val(d.style);
        row.find('input[name="max_width"]').val(d.max_width);
        row.find('input[name="x"]').val(d.x);
        row.find('input[name="y"]').val(d.y);
    }

    toSerializedRow(row) {
        row = $(row);
        return {
            caption: row.find('input[name="caption"]').val(),
            style: row.find('select[name="style"]').val(),
            max_width: parseInt(row.find('input[name="max_width"]').val(), 10),
            x: parseInt(row.find('input[name="x"]').val(), 10),
            y: parseInt(row.find('input[name="y"]').val(), 10),
        };
    }
}

export {TableField};
export {ReferenceLineField};
export {ReferenceRangeField};
export {ReferenceLabelField};
