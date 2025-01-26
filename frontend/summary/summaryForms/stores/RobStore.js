import _ from "lodash";
import {action, computed, observable} from "mobx";
import {toJS} from "mobx";
import h from "shared/utils/helpers";
const _getDefaultSettings = function() {
    return {
        title: "",
        xAxisLabel: "",
        yAxisLabel: "",
        padding_top: 20,
        padding_right: 20,
        padding_bottom: 20,
        padding_left: 20,
        cell_size: 10,
        x_field: "study",
        sort_order: "short_citation",
        study_label_field: "short_citation",
        included_metrics: [],
        excluded_score_ids: [],
        show_legend: true,
        show_na_legend: false,
        show_nr_legend: false,
        legend_x: 5,
        legend_y: 5,
    };
};

class RobStore {
    constructor(rootStore) {
        this.root = rootStore;
    }
    @observable settings = null;

    getDefaultSettings() {
        return _getDefaultSettings();
    }

    @action.bound changeSetting(path, value) {
        _.set(this.settings, path, value);
        console.log(toJS(this.settings));
    }

    @action setFromJsonSettings(settings, firstTime) {
        this.settings = settings;
    }

    @computed get settingsHash() {
        return h.hashString(JSON.stringify(this.settings));
    }

    // active tab
    @observable activeTab = 0;
    @action.bound changeActiveTab(index) {
        this.activeTab = index;
        return true;
    }
}

export default RobStore;
