import _ from "lodash";

import {NULL_CASE} from "../shared";

class ColumnSelect {
    constructor(mgr, showBlank, attrs) {
        this.mgr = mgr;
        this.showBlank = showBlank;
        this.select = $('<select class="form-control">');
        if (attrs) {
            _.forEach(attrs, (v, k) => this.select.attr(k, v));
        }
        this.update();
    }
    update() {
        const selectedValue = this.select.find("option:selected").val(),
            opts = this.mgr.headers.map(v => `<option value="${v}">${v}</option>`);
        if (this.showBlank) {
            opts.unshift(`<option value="${NULL_CASE}">${NULL_CASE}</option>`);
        }
        this.select.html(opts.concat());
        if (selectedValue) {
            this.select.find(`option[value="${selectedValue}"]`).prop("selected", true);
        }
    }
}
class ColumnSelectManager {
    constructor(data_pivot) {
        this.data_pivot = data_pivot;
        this.selects = [];
        this.updateHeaders();
    }
    createSelect(showBlank, attrs) {
        const select = new ColumnSelect(this, showBlank, attrs);
        this.selects.push(select);
        return select.select;
    }
    updateSelects() {
        this.updateHeaders();
        this.selects.forEach(select => select.update());
    }
    updateHeaders() {
        const firstRow = this.data_pivot.data[0],
            headers = _.keys(firstRow);
        headers.push(
            ...this.data_pivot.settings.calculated_columns
                .filter(d => d.name.length > 0)
                .map(d => d.name)
        );
        this.headers = headers;
        this.data_pivot.store.sortStore.updateFieldColumns(headers);
    }
}

export default ColumnSelectManager;
