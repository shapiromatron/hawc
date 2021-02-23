import _ from "lodash";
import {action, computed, observable} from "mobx";
import h from "shared/utils/helpers";

import {TableType} from "../constants";
import GenericTableStore from "../genericTable/store";

const getTableStore = function(table) {
    if (table.table_type == TableType.GENERIC) {
        return new GenericTableStore(false, table.content);
    } else {
        throw "Unknown table type";
    }
};

class SummaryTableViewStore {
    @observable table = null;

    constructor(config) {
        this.config = config;
        this.table = null;
        this.tableStore = null;
    }

    @computed get hasTable() {
        return _.isObject(this.table);
    }

    @action.bound fetchTable() {
        const url = `/summary/api/summary-table/${this.config.table_id}/`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.tableStore = getTableStore(json);
                this.table = json;
            })
            .catch(ex => console.error("Table fetch failed", ex));
    }
}

export default SummaryTableViewStore;
