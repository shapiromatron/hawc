import {NULL_CASE} from "../shared";

class ColumnSelect {
    constructor(data_pivot, showBlank) {
        this.data_pivot = data_pivot;
        this.showBlank = showBlank;
        this.select = $('<select class="form-control">');
        this.update();
    }
    update() {
        const selectedValue = this.select.find("option:selected").val(),
            opts = this.data_pivot.data_headers.map(v => `<option value="${v}">${v}</option>`);
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
    }
    createSelect(showBlank) {
        const select = new ColumnSelect(this.data_pivot, showBlank);
        this.selects.push(select);
        return select.select;
    }
    updateSelects() {
        this.data_pivot.set_data_headers();
        this.selects.forEach(select => select.update());
    }
}

export default ColumnSelectManager;
