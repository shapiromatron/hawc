import * as d3 from "d3";
import {action, computed, observable, toJS} from "mobx";

class VocabBrowseStore {
    @observable query = "";

    constructor(config) {
        this.config = config;
        this.dataset = d3.csvParse(config.data, (d, i) => {
            // make numbers in data numeric if possible
            // see https://github.com/mbostock/d3/wiki/CSV
            for (var field in d) {
                d[field] = +d[field] || d[field];
            }
            d._key = i;
            d._searchString = `${d.system} ${d.organ} ${d.effect} ${d.effect_subtype} ${d.name}`.toLocaleLowerCase();
            return d;
        });
    }

    @computed get filteredDataset() {
        const text = toJS(this.query).toLocaleLowerCase();
        if (text === "") {
            return this.dataset;
        }
        return this.dataset.filter(d => d._searchString.includes(text));
    }

    @action.bound updateQuery(value) {
        this.query = value;
    }
}

export default VocabBrowseStore;
