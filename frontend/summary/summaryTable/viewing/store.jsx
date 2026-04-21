import _ from "lodash";
import {action, computed, makeObservable, observable} from "mobx";
import h from "shared/utils/helpers";

import {getTableStore} from "../lookups";

class SummaryTableViewStore {
    @observable table = null;

    constructor(config) {
        makeObservable(this);
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
