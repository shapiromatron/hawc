import _ from "lodash";
import {action, computed, makeObservable, observable, toJS} from "mobx";
import TableFootnotes from "shared/utils/TableFootnotes";

import Endpoint from "../Endpoint";

const orderings = {0: undefined, 1: "asc", 2: "desc"},
    sortings = {
        name: d => d.data.name,
        organ: d => d.data.organ,
        time: d => d.data.observation_time,
    };

class AnimalGroupTableStore {
    @observable endpoints = [];
    @observable sortKey = "name";
    @observable sortValue = 1;

    constructor(data) {
        makeObservable(this);
        this.endpoints = data.endpoints.map(d => new Endpoint(d));
        this.footnotes = new TableFootnotes();
    }

    @action.bound cycleSort(key) {
        if (key == this.sortKey) {
            let nextSortValue = this.sortValue + 1;
            if (nextSortValue === 3) {
                this.sortKey = null;
                this.sortValue = 0;
            } else {
                this.sortValue = nextSortValue;
            }
        } else {
            this.sortKey = key;
            this.sortValue = 1;
        }
    }

    @computed get hasEndpoints() {
        return this.endpoints.length > 0;
    }

    @computed get endpointsNoDr() {
        return this.endpoints.filter(endpoint => !endpoint.hasEGdata());
    }

    @computed get endpointsDr() {
        const orders = [],
            directions = [];

        if (this.sortKey) {
            orders.push(sortings[this.sortKey]);
            directions.push(orderings[this.sortValue]);
        }

        return _.chain(this.endpoints)
            .filter(endpoint => endpoint.hasEGdata())
            .orderBy(orders, directions)
            .value();
    }

    @computed get firstEndpoint() {
        return this.endpointsDr[0];
    }

    @computed get doses() {
        return this.firstEndpoint.doseUnits.activeDoses;
    }

    @computed get numCols() {
        return this.doses.length + 3;
    }

    @computed get units() {
        return this.firstEndpoint.doseUnits.units;
    }

    @computed get endpointsByN() {
        let mapping = _.chain(toJS(this.endpointsDr))
            .map(endpoint => {
                const key = endpoint.data.groups.map((d, i) => d.n || `NR-${i}`).join("|");
                return {key, endpoint};
            })
            .groupBy("key")
            .values()
            .map(items => items.map(d => d.endpoint))
            .value();
        return mapping;
    }
}

export default AnimalGroupTableStore;
