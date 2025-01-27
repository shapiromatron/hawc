import _ from "lodash";
import {action, computed, observable} from "mobx";
import h from "shared/utils/helpers";

const _getDefaultSettings = function(visual_type, metrics) {
    if (visual_type === 2) {
        return {
            title: "",
            xAxisLabel: "",
            yAxisLabel: "",
            padding_top: 20,
            padding_right: 330,
            padding_bottom: 35,
            padding_left: 20,
            cell_size: 40,
            x_field: "study",
            sort_order: "short_citation",
            study_label_field: "short_citation",
            included_metrics: metrics,
            excluded_score_ids: [],
            show_legend: true,
            show_na_legend: true,
            show_nr_legend: true,
            legend_x: 9999,
            legend_y: 9999,
        };
    } else if (visual_type === 3) {
        return {
            title: "Title",
            xAxisLabel: "Percent of studies",
            yAxisLabel: "",
            padding_top: 40,
            padding_right: 330,
            padding_bottom: 40,
            padding_left: 70,
            plot_width: 400,
            row_height: 30,
            show_values: true,
            included_metrics: metrics,
            excluded_score_ids: [],
            show_legend: true,
            show_na_legend: true,
            show_nr_legend: true,
            legend_x: 9999,
            legend_y: 9999,
        };
    }
};

class RobStore {
    constructor(rootStore) {
        this.root = rootStore;
        this.visual_type = this.root.base.config.visual_type;
        this.metrics = this.root.base.config.rob_config.metrics;
        this.scores = this.root.base.config.rob_config.scores;
    }
    @observable settings = null;
    getDefaultSettings() {
        const metrics = this.metrics.map(d => d.id);
        return _getDefaultSettings(this.visual_type, metrics);
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
    @computed get isHeatmap() {
        return this.visual_type === 2;
    }
    @computed get isBarchart() {
        return this.visual_type === 3;
    }
    @action.bound changeSetting(path, value) {
        _.set(this.settings, path, value);
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
            payload = this.root.base.toJsonObject();
        payload["visual_type"] = config.visual_type;
        payload["evidence_type"] = config.initial_data.evidence_type;
        h.handleSubmit(
            url,
            "POST",
            config.csrf,
            payload,
            response => {
                console.log(response);
                this.currentDataHash = this.visualDataHash;
                this.visualData = response;
                this.dataFetchRequired = false;
            },
            err => {
                console.error(err);
            },
            err => {
                console.error(err);
            }
        );
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
        const settings = this.root.base.toJsonObject();
        _.each(["title", "slug", "caption", "settings", "published"], d => delete settings[d]);
        return h.hashString(JSON.stringify(settings));
    }
    // active tab
    @observable activeTab = 0;
    @action.bound changeActiveTab(index) {
        this.activeTab = index;
        return true;
    }
}

export default RobStore;
