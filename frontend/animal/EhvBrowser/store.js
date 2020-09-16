import * as d3 from "d3";
import {action, toJS, observable} from "mobx";

class EhvBrowseStore {
    @observable query = "";
    @observable filteredDataset = null;
    @observable isFiltering = true;

    constructor(config) {
        this.config = config;
        this.dataset = d3.csvParse(config.data, (d, i) => {
            // make numbers in data numeric if possible
            // see https://github.com/mbostock/d3/wiki/CSV
            for (var field in d) {
                d[field] = +d[field] || d[field];
            }
            d._key = i;
            return d;
        });
        this.filteredDataset = this.dataset;
    }

    @action.bound filterDataset() {
        const text = toJS(this.query);
        if (text === "") {
            this.filteredDataset = this.dataset;
            this.isFiltering = false;
            return;
        }
        this.isFiltering = true;
        // use a setTimeout to make async
        setTimeout(() => {
            this.filteredDataset = this.dataset.filter(
                d =>
                    d.system.toLocaleLowerCase().includes(text) ||
                    d.endpoint_name.toLocaleLowerCase().includes(text) ||
                    d.organ.toLocaleLowerCase().includes(text) ||
                    d.effect.toLocaleLowerCase().includes(text) ||
                    d.effect_subtype.toLocaleLowerCase().includes(text)
            );
            this.isFiltering = false;
        }, 1);
    }

    @action.bound updateQuery(value) {
        this.query = value;
    }
}

export default EhvBrowseStore;
