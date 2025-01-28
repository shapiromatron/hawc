import {action, computed, observable} from "mobx";
import h from "shared/utils/helpers";

class BaseDjangoStore {
    // Custom Store where the Form is rendered by Django, not React.
    constructor(rootStore, config) {
        this.root = rootStore;
        this.config = config;
    }

    config = null;
    @observable currentTab = 0;
    @observable refetchDataRequired = false;

    @action setInitialData() {
        const {initial_data} = this.config,
            settings =
                Object.keys(initial_data.settings).length > 0
                    ? initial_data.settings
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
    @action.bound toJsonObject() {
        return h.formToJsonObject(this.djangoForm);
    }
    @action.bound toFormData() {
        return new FormData(this.djangoForm);
    }
    @computed get isCreate() {
        return this.config.crud === "Create";
    }
    @computed get settingsHash() {
        return h.hashString(this.settingsField.value);
    }
}

export default BaseDjangoStore;
