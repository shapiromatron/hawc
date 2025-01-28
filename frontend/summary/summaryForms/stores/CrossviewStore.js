import _ from "lodash";
import {action, computed, observable} from "mobx";
import {
    deleteArrayElement,
    moveArrayElementDown,
    moveArrayElementUp,
} from "shared/components/EditableRowData";
import h from "shared/utils/helpers";

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
    createFilter = function() {
        return {
            name: "",
            headerName: "",
            allValues: true,
            values: [],
            column: 1,
            x: 0,
            y: 0,
        };
    },
    createReflines = function() {
        return {
            value: 1,
            title: "",
            style: "",
        };
    },
    createRefranges = function() {
        return {
            lower: 1,
            upper: 2,
            title: "",
            style: "",
        };
    },
    createLabels = function() {
        return {
            caption: "",
            style: "",
            max_width: 0,
            x: 0,
            y: 0,
        };
    },
    createColorFilters = function() {
        return {
            value: "",
            headerName: "",
            color: "#000000",
        };
    },
    createEndpointFilters = function() {
        return {
            field: "",
            filterType: "",
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
    @computed get metricTableData() {
        const selectedMetrics = new Set(this.settings.included_metrics);
        return this.metrics.map(d => {
            return {id: d.id, selected: selectedMetrics.has(d.id), name: d.name};
        });
    }
    @computed get excludedScoreData() {
        return {
            excluded: new Set(this.settings.excluded_score_ids),
            scores: this.scores,
        };
    }
    @action.bound changeSetting(path, value) {
        _.set(this.settings, path, value);
    }
    @action.bound createArrayElement(type) {
        switch (type) {
            case "filters":
                this.settings.filters.push(createFilter());
                break;
            case "reflines_dose":
                this.reflines_dose.push(createReflines());
                break;
            case "refranges_dose":
                this.refranges_dose.push(createRefranges());
                break;
            case "reflines_response":
                this.reflines_response.push(createReflines());
                break;
            case "refranges_response":
                this.refranges_response.push(createRefranges());
                break;
            case "labels":
                this.labels.push(createLabels());
                break;
            case "colorFilters":
                this.colorFilters.push(createColorFilters());
                break;
            case "endpointFilters":
                this.endpointFilters.push(createEndpointFilters());
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
    @action.bound toggleMetricInclusion(id, include) {
        const set = new Set(this.settings.included_metrics);
        include ? set.add(id) : set.delete(id);
        this.settings.included_metrics = Array.from(set).sort();
    }
    @action.bound toggleExcludedScores(id, include) {
        const set = new Set(this.settings.excluded_score_ids);
        include ? set.delete(id) : set.add(id);
        this.settings.excluded_score_ids = Array.from(set);
    }
    @action setFromJsonSettings(settings, firstTime) {
        this.settings = settings;
    }
    @computed get settingsHash() {
        return h.hashString(JSON.stringify(this.settings));
    }

    // visualization data
    @observable visualData = null;
    @action.bound getVisualData() {
        const {config} = this.root.base,
            url = `/summary/api/assessment/${config.assessment}/json_data/`,
            formData = this.root.base.toFormData();
        formData.append("visual_type", config.visual_type);
        formData.append("evidence_type", config.initial_data.evidence_type);

        fetch(url, h.fetchPostForm(config.csrf, formData))
            .then(resp => resp.json())
            .then(response => {
                response.settings = this.settings;
                this.currentDataHash = this.visualDataHash;
                this.visualData = response;
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
    // active tab
    @observable activeTab = 0;
    @action.bound changeActiveTab(index) {
        this.activeTab = index;
        return true;
    }
}

export default CrossviewStore;
