import * as d3 from "d3";
import {action, computed, toJS, observable} from "mobx";

class EhvBrowseStore {
    @observable query = "";

    constructor(config) {
        this.config = config;
        this.dataset = d3.csvParse(config.data, d => {
            // make numbers in data numeric if possible
            // see https://github.com/mbostock/d3/wiki/CSV
            for (var field in d) {
                d[field] = +d[field] || d[field];
            }
            return d;
        });
    }

    @action.bound updateQuery(value) {
        this.query = value;
    }

    @computed get filteredDataset() {
        const text = toJS(this.query);
        if (text === "") {
            return this.dataset;
        }
        return this.dataset.filter(
            d =>
                d.system.toLocaleLowerCase().includes(text) ||
                d.endpoint_name.toLocaleLowerCase().includes(text) ||
                d.organ.toLocaleLowerCase().includes(text) ||
                d.effect.toLocaleLowerCase().includes(text) ||
                d.effect_subtype.toLocaleLowerCase().includes(text)
        );
    }
}

export default EhvBrowseStore;
