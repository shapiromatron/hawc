import Endpoint from "animal/Endpoint";
import _ from "lodash";
import {action, computed, observable} from "mobx";
import {
    deleteArrayElement,
    moveArrayElementDown,
    moveArrayElementUp,
} from "shared/components/EditableRowData";
import h from "shared/utils/helpers";

import CrossviewPlot from "../../summary/CrossviewPlot";
import D3Visualization from "../../summary/D3Visualization";
import {
    DATA_FILTER_CONTAINS,
    DATA_FILTER_OPTIONS,
    readableCustomQueryFilters,
} from "../../summary/filters";

const _getDefaultSettings = function() {
        return {
            title: "",
            xAxisLabel: "Dose (<add units>)",
            yAxisLabel: "% change from control (continuous), % incidence (dichotomous)",
            width: 1100,
            height: 600,
            inner_width: 940,
            inner_height: 520,
            padding_left: 75,
            padding_top: 45,
            dose_isLog: true,
            dose_range: "",
            response_range: "",
            title_x: 0,
            title_y: 0,
            xlabel_x: 0,
            xlabel_y: 0,
            ylabel_x: 0,
            ylabel_y: 0,
            filters: [],
            reflines_dose: [],
            refranges_dose: [],
            reflines_response: [],
            refranges_response: [],
            labels: [],
            colorBase: "#cccccc",
            colorHover: "#ff4040",
            colorSelected: "#6495ed",
            colorFilters: [],
            colorFilterLegend: true,
            colorFilterLegendLabel: "Color filters",
            colorFilterLegendX: 0,
            colorFilterLegendY: 0,
            endpointFilters: [],
            endpointFilterLogic: "and",
            filtersQuery: "",
        };
    },
    createFilter = function(field) {
        return {
            name: field.id,
            headerName: field.label,
            allValues: true,
            values: [],
            column: 1,
            x: 0,
            y: 0,
        };
    },
    createReflines = function(style) {
        return {
            value: 1,
            title: "",
            style: style.id,
        };
    },
    createRefranges = function(style) {
        return {
            lower: 1,
            upper: 2,
            title: "",
            style: style.id,
        };
    },
    createLabels = function(style) {
        return {
            caption: "",
            style: style.id,
            max_width: 150,
            x: 0,
            y: 0,
        };
    },
    createColorFilters = function(field) {
        return {
            field: field.id,
            value: "",
            headerName: field.label,
            color: "#8BA870",
        };
    },
    createEndpointFilters = function(field, filter) {
        return {
            field: field.id,
            filterType: DATA_FILTER_CONTAINS,
            value: "",
        };
    };

class CrossviewStore {
    constructor(rootStore) {
        this.root = rootStore;
    }
    @observable settings = null;
    getDefaultSettings() {
        return _getDefaultSettings();
    }
    @action.bound changeSetting(path, value) {
        _.set(this.settings, path, value);
    }
    @action.bound createArrayElement(type) {
        switch (type) {
            case "filters":
                this.settings.filters.push(createFilter(this.fieldChoices[0]));
                break;
            case "reflines_dose":
                this.settings.reflines_dose.push(createReflines(this.lineStyleChoices[0]));
                break;
            case "refranges_dose":
                this.settings.refranges_dose.push(createRefranges(this.rectangleStyleChoices[0]));
                break;
            case "reflines_response":
                this.settings.reflines_response.push(createReflines(this.lineStyleChoices[0]));
                break;
            case "refranges_response":
                this.settings.refranges_response.push(
                    createRefranges(this.rectangleStyleChoices[0])
                );
                break;
            case "labels":
                this.settings.labels.push(createLabels(this.textStyleChoices[0]));
                break;
            case "colorFilters":
                this.settings.colorFilters.push(createColorFilters(this.fieldChoices[0]));
                break;
            case "endpointFilters":
                this.settings.endpointFilters.push(createEndpointFilters(this.fieldChoices[0]));
                break;
        }
    }
    @action.bound deleteArrayElement(type, index) {
        deleteArrayElement(this.settings[type], index);
    }
    @action.bound moveArrayElementUp(type, index) {
        moveArrayElementUp(this.settings[type], index);
    }
    @action.bound moveArrayElementDown(type, index) {
        moveArrayElementDown(this.settings[type], index);
    }
    @action setFromJsonSettings(settings, firstTime) {
        this.settings = settings;
    }
    @computed get settingsHash() {
        return h.hashString(JSON.stringify(this.settings));
    }

    // visualization data
    @observable formData = null;
    @observable visualData = null;
    @observable visualDataFetching = false;
    @action.bound getVisualData() {
        const {config} = this.root.base,
            url = `/summary/api/assessment/${config.assessment}/json_data/`,
            formData = this.root.base.toFormData();
        formData.append("visual_type", config.visual_type);
        formData.append("evidence_type", config.evidence_type);

        if (this.visualDataFetching) {
            return;
        }
        this.visualDataFetching = true;
        fetch(url, h.fetchPostForm(config.csrf, formData))
            .then(resp => resp.json())
            .then(response => {
                response.settings = this.settings;
                this.visualDataFetching = false;
                this.currentDataHash = this.visualDataHash;
                this.visualData = response;

                const formData = _.cloneDeep(response);
                formData.endpoints = formData.endpoints.map(d => {
                    var e = new Endpoint(d);
                    e.doseUnits.activate(formData.dose_units);
                    return e;
                });
                this.formData = formData;

                this.dataFetchRequired = false;
            });
    }

    // check if visualization data is needed
    @observable currentDataHash = null;
    @observable dataFetchRequired = true;
    @action.bound checkDataHash() {
        if (this.currentDataHash == null || this.currentDataHash != this.visualDataHash) {
            this.dataFetchRequired = true;
            this.getVisualData();
        }
    }
    @computed get visualDataHash() {
        // compute settings hash for if we have the correct data to build the visual
        const settings = this.root.base.toFormData();
        _.each(["title", "slug", "caption", "settings", "published"], d => delete settings[d]);
        const params = new URLSearchParams(settings).toString();
        return h.hashString(params);
    }

    // endpoint field options
    @computed get fieldChoices() {
        return _.map(CrossviewPlot._filters, (k, v) => {
            return {id: v, label: k};
        });
    }
    @computed get fieldOptionChoices() {
        const options = {};
        _.keys(CrossviewPlot._filters).forEach(key => {
            const func = CrossviewPlot._cw_filter_process[key];
            options[key] = _.chain(this.formData.endpoints)
                .map(endpoint => func(endpoint))
                .flatten()
                .uniq()
                .filter(d => d.length > 0)
                .map(d => {
                    return {id: d, label: d};
                })
                .value();
        });
        return options;
    }
    @computed get lineStyleChoices() {
        return D3Visualization.styles.lines.map(d => {
            return {id: d.name, label: d.name};
        });
    }
    @computed get rectangleStyleChoices() {
        return D3Visualization.styles.rectangles.map(d => {
            return {id: d.name, label: d.name};
        });
    }
    @computed get textStyleChoices() {
        return D3Visualization.styles.texts.map(d => {
            return {id: d.name, label: d.name};
        });
    }
    @computed get filtersQueryReadable() {
        const filters = this.settings.endpointFilters,
            optMap = _.keyBy(DATA_FILTER_OPTIONS, "id");
        return readableCustomQueryFilters(this.settings.filtersQuery, i => {
            const filter = filters[i - 1], // convert 1 to 0 indexing
                valStr = _.isNaN(_.toNumber(filter.value))
                    ? `"${filter.value}"`
                    : `${filter.value}`;
            return `"${filter.field}" ${optMap[filter.filterType].label} ${valStr} {${i}}`;
        });
    }

    // active tab
    @observable activeTab = 0;
    @action.bound changeActiveTab(index) {
        this.activeTab = index;
        return true;
    }
}

export default CrossviewStore;
