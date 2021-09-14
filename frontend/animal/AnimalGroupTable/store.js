import _ from "lodash";
import {computed, toJS, observable} from "mobx";

import TableFootnotes from "shared/utils/TableFootnotes";
import Endpoint from "../Endpoint";

class AnimalGroupTableStore {
    @observable endpoints = [];

    constructor(data) {
        this.endpoints = data.endpoints.map(d => new Endpoint(d));
        this.footnotes = new TableFootnotes();
    }

    @computed get hasEndpoints() {
        return this.endpoints.length > 0;
    }

    @computed get endpointsNoDr() {
        return this.endpoints.filter(endpoint => !endpoint.hasEGdata());
    }

    @computed get endpointsDr() {
        return this.endpoints.filter(endpoint => endpoint.hasEGdata());
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
