import _ from "lodash";
import {action, computed, makeObservable, observable, toJS} from "mobx";
import h from "shared/utils/helpers";

const CRITICAL_VALUES = ["noel", "loel", "fel", "bmd", "bmdl"];

class EndpointListStore {
    config = null;

    @observable rawDataset = null;

    @observable settings = null;

    @observable doseOptions = null;
    @observable systemOptions = null;
    @observable criticalValueOptions = null;

    constructor(config) {
        makeObservable(this);
        this.config = config;
        this.getDataset();
    }
    @computed get filteredData() {
        if (this.rawDataset === null) {
            return null;
        }
        return _.chain(toJS(this.rawDataset))
            .filter(d => _.includes(this.settings.doses, d["dose units id"]))
            .filter(d => _.includes(this.settings.systems, d.system))
            .filter(d => _.some(this.settings.criticalValues.filter(val => d[val] !== null)))
            .value();
    }
    @computed get plotData() {
        if (this.filteredData === null) {
            return null;
        }
        return _.chain(toJS(this.rawDataset))
            .map(d => {
                return this.settings.criticalValues.map(type => {
                    return {data: d, dose: d[type], type};
                });
            })
            .flatten()
            .filter(d => d.dose !== null && d.dose > 0)
            .sortBy("dose")
            .value();
    }

    @computed get hasDataset() {
        return this.dataset !== null;
    }

    @action.bound getDataset() {
        const {data_url} = this.config;
        fetch(data_url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.getDefaultSettings(json);
                this.rawDataset = json;
            });
    }
    @action.bound getDefaultSettings(dataset) {
        const doseOptions = _.chain(dataset)
                .map(d => {
                    return {id: d["dose units id"], label: d["dose units name"]};
                })
                .uniqBy(d => d.id)
                .value(),
            systemOptions = _.chain(dataset)
                .map(d => {
                    return {id: d.system, label: d.system || h.nullString};
                })
                .uniqBy(d => d.id)
                .sortBy(d => d.id.toLowerCase())
                .value(),
            criticalValueOptions = CRITICAL_VALUES.map(d => {
                return {id: d, label: d};
            }),
            settings = {
                doses: doseOptions.map(d => d.id),
                systems: systemOptions.map(d => d.id),
                criticalValues: criticalValueOptions.map(d => d.id),
                approximateXValues: true,
            };

        this.settings = settings;
        this.doseOptions = doseOptions;
        this.systemOptions = systemOptions;
        this.criticalValueOptions = criticalValueOptions;
    }
    @action.bound changeSettingsSelection(key, value) {
        this.settings[key] = value;
    }
}

export default EndpointListStore;
