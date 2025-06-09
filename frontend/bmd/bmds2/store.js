import Endpoint from "animal/Endpoint";
import {applyRecommendationLogic} from "bmd/common/recommendationLogic";
import _ from "lodash";
import {action, autorun, computed, observable} from "mobx";

import h from "/shared/utils/helpers";

import {BMR_MODAL_ID, OPTION_MODAL_ID, OUTPUT_MODAL_ID} from "./constants";

class Bmd2Store {
    constructor(config) {
        this.config = config;
    }

    @observable hasExecuted = false;
    @observable isReady = false;
    @observable endpoint = null;
    @observable dataType = null;
    @observable session = null;
    @observable doseUnits = null;
    @observable models = [];
    @observable modelSettings = [];
    @observable selectedModelOptionIndex = null;
    @observable selectedModelOption = null;
    @observable bmrs = [];
    @observable selectedBmrIndex = null;
    @observable selectedBmr = null;
    @observable allModelOptions = [];
    @observable allBmrOptions = null;
    @observable selectedOutputs = [];
    @observable hoverModel = null;
    @observable selectedModelId = null;
    @observable selectedModelNotes = "";
    @observable logic = [];

    // actions

    // fetch-settings
    @action.bound fetchEndpoint(_id) {
        const url = `/ani/api/endpoint/${this.config.endpoint_id}/`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                const endpoint = new Endpoint(json);
                this.dataType = endpoint.data.data_type;
                // do endpoint last; this triggers other side effects
                this.endpoint = endpoint;
            })
            .catch(ex => console.error("Endpoint parsing failed", ex));
    }
    @action.bound fetchSessionSettings(callback) {
        const url = this.config.session_url;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(settings => {
                // add key-prop to each values dict for parameter
                _.each(settings.model_options, d => _.each(d.defaults, (v, k) => (v.key = k)));

                // create model-settings
                // 1) only get the first bmr instance of the model
                // 2) add defaults based on the model name
                const modelSettingsMap = _.keyBy(settings.model_options, "name");
                settings.outputs.models.forEach(d => {
                    d.defaults = modelSettingsMap[d.name].defaults;
                    d.dose_units = settings.dose_units;
                });

                const modelSettings = _.chain(settings.outputs.models)
                    .filter(d => d.bmr_index === 0)
                    .map(d => h.deepCopy(d))
                    .value();

                // set store features
                this.models = settings.outputs.models;
                this.modelSettings = modelSettings;
                this.bmrs = settings.inputs.bmrs;
                this.doseUnits = settings.dose_units;
                this.allModelOptions = settings.model_options;
                this.allBmrOptions = _.keyBy(settings.bmr_options, "type");
                this.logic = settings.logic;
                this.hasExecuted = settings.is_finished;

                if (settings.selected) {
                    this.selectedModelId = settings.selected.model_id;
                    this.selectedModelNotes = settings.selected.notes;
                } else {
                    this._resetSelectedModel();
                }

                // do session last; this triggers other side effects
                this.session = settings;

                if (callback) {
                    callback();
                }
            })
            .catch(ex => console.error("Endpoint parsing failed", ex));
    }
    @action.bound _resetSelectedModel() {
        this.selectedModelId = null;
        this.selectedModelNotes = "";
    }
    @action.bound applyRecommendationLogic() {
        if (this.hasExecuted) {
            applyRecommendationLogic(this.logic, this.models, this.endpoint, this.doseUnits);
        }
        this.isReady = true;
    }
    autoApplyRecommendationLogic = autorun(() => {
        if (this.hasSession && this.hasEndpoint) {
            this.applyRecommendationLogic();
        }
    });

    // ui settings
    @action.bound showModal(name) {
        // wait until the modal element is rendered in the DOM before triggering show modal
        let waitedFor = 0;
        const waitInterval = 20,
            maxWait = 1000,
            selector = `#${name}`,
            tryShow = () => {
                waitedFor += waitInterval;
                if ($(selector).length > 0 && !$(selector).hasClass("in")) {
                    $(selector).modal("show");
                } else {
                    if (waitedFor < maxWait) {
                        setTimeout(tryShow, waitInterval);
                    }
                }
            };
        setTimeout(tryShow, waitInterval);
    }
    @action.bound showOptionModal(modelIndex) {
        this.selectedModelOptionIndex = modelIndex;
        this.selectedModelOption = this.modelSettings[modelIndex];
        this.showModal(OPTION_MODAL_ID);
    }
    @action.bound showBmrModal(index) {
        this.selectedBmrIndex = index;
        this.selectedBmr = this.bmrs[index];
        this.showModal(BMR_MODAL_ID);
    }
    @action.bound showOutputModal(models) {
        this.selectedOutputs = models;
        this.showModal(OUTPUT_MODAL_ID);
    }

    // outputs
    @action.bound setHoverModel(model) {
        this.hoverModel = model;
    }

    @computed get hasEndpoint() {
        return this.endpoint !== null;
    }
    @computed get hasSession() {
        return this.session !== null;
    }
}

export default Bmd2Store;
