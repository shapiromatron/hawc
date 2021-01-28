import _ from "lodash";
import {action, computed, observable, toJS} from "mobx";
import h from "shared/utils/helpers";

class SummaryTableViewStore {
    @observable table = null;
    @observable cells = null;

    constructor(config) {
        this.config = config;
    }

    @computed get hasTable() {
        return _.isObject(this.table);
    }

    @computed get hasCells() {
        return _.isObject(this.cells);
    }

    @action.bound fetchTable() {
        const url = `/summary/api/summary-table/${this.config.table_id}/`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.table = json;
            })
            .catch(ex => console.error("Table fetch failed", ex));
    }

    @action.bound fetchCells() {
        const url = `/summary/api/summary-table/${this.config.table_id}/cells`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.cells = json;
            })
            .catch(ex => console.error("Cells fetch failed", ex));
    }

    CELL_ENUM = {
        CELL: 1,
        EMPTY: 2,
        SKIP: 3,
    };

    @computed get rowOrderEnums() {
        const {content} = this.table,
            {rows, columns, cells} = toJS(content);
        let enums = Array(rows * columns).fill(this.CELL_ENUM.EMPTY);
        for (let cell of cells) {
            let cellIndex = cell.row * columns + cell.column;
            for (let r = 0; r < cell.row_span; r++) {
                for (let c = 0; c < cell.col_span; c++) {
                    let index = cellIndex + c + r * columns;
                    enums[index] = this.CELL_ENUM.SKIP;
                }
            }
            enums[cellIndex] = this.CELL_ENUM.CELL;
        }
        return enums;
    }
}

export default SummaryTableViewStore;
