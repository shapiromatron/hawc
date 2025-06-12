import {action, computed, makeObservable, observable} from "mobx";
import h from "shared/utils/helpers";

class BaseStore {
    constructor(rootStore, config) {
        makeObservable(this);
        this.root = rootStore;
        this.config = config;
    }

    config = null;
    djangoForm = null;
    settingsField = null;
    currentTab = 0;

    @observable dataError = null;
    @observable isFetchingData = false;
    @observable dataUrl = null;
    @observable dataRefreshRequired = false;
    @observable dataset = null;
    @observable djangoFormData = {};

    @action setInitialData() {
        const {initial_settings} = this.config,
            settings =
                Object.keys(initial_settings).length > 0
                    ? initial_settings
                    : this.root.subclass.getDefaultSettings();
        this.updateDjangoSettings(settings);
        this.updateReactSettings(true);
    }
    @action setDjangoForm = djangoForm => {
        this.djangoForm = djangoForm;
        this.settingsField = djangoForm.querySelector("#id_settings");
    };
    @action.bound handleSubmit() {
        this.updateDjangoSettings(this.root.subclass.settings);
        this.djangoForm.submit();
    }
    @action.bound updateDjangoSettings(settings) {
        this.settingsField.value = JSON.stringify(settings, null, 2);
    }
    @action.bound updateReactSettings(firstTime) {
        const settings = JSON.parse(this.settingsField.value);
        this.root.subclass.setFromJsonSettings(settings, firstTime);
    }
    @action.bound toFormData() {
        return new FormData(this.djangoForm);
    }
    @action.bound handleTabChange(newIndex, lastIndex) {
        // make sure that data cross tabs are synced
        this.currentTab = newIndex;
        switch (lastIndex) {
            case 0:
                this.updateReactSettings(false);
                break;
            default:
                this.updateDjangoSettings(this.root.subclass.settings);
                break;
        }
    }

    @action.bound getDataset() {
        this.isFetchingData = true;
        fetch(this.dataUrl, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.dataset = json;
                this.dataRefreshRequired = false;
                this.root.subclass.afterGetDataset();
            })
            .catch(error => {
                this.setDataError(error);
            })
            .finally(() => {
                this.isFetchingData = false;
            });
    }
    @action.bound setDataError(dataError) {
        this.dataError = dataError;
    }
    @action setDataRefreshRequired() {
        this.dataRefreshRequired = true;
    }
    @computed get hasDataset() {
        return this.dataset !== null;
    }
    @computed get isDataReady() {
        return this.hasDataset && !this.dataRefreshRequired;
    }
    @computed get canFetchData() {
        return this.dataUrl && this.dataUrl.length > 0;
    }
    @computed get isCreate() {
        return this.config.crud === "Create";
    }
    @computed get settingsHash() {
        return h.hashString(this.settingsField.value);
    }
}

export default BaseStore;
