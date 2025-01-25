import _ from "lodash";
import {action, computed, observable} from "mobx";
import {deleteArrayElement} from "shared/components/EditableRowData";
import h from "shared/utils/helpers";
import {NULL_VALUE} from "summary/summary/constants";

const _getDefaultSettings = function() {
    return {};
};

class RobStore {
    constructor(rootStore) {
        this.root = rootStore;
        this.getDataset();
    }
    @observable settings = null;

    getDefaultSettings() {
        return _getDefaultSettings();
    }

    @action.bound changeSettings(path, value) {
        _.set(this.settings, path, value);
    }

    @action setFromJsonSettings(settings, firstTime) {
        this.settings = settings;
    }

    @action.bound getDataset() {
        const {config} = this.root.base,
            payload = {config: {visual_type: config.visual_type}};
        h.handleSubmit(
            config.api_data_url,
            "POST",
            config.csrf,
            payload,
            response => {
                this.data = response;
            },
            err => console.error(err),
            err => console.error(err)
        );
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
