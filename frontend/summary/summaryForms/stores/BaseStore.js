import $ from "$";
import {observable, action, computed} from "mobx";

import h from "shared/utils/helpers";

const TABS = {
    OVERALL: 0,
    DATA: 1,
    CUSTOMIZATION: 2,
    PREVIEW: 3,
};

class BaseStore {
    constructor(rootStore, config) {
        this.root = rootStore;
        this.config = config;
    }

    config = null;
    djangoForm = null;
    currentTab = 0;

    @observable dataError = null;
    @observable isFetchingData = false;
    @observable dataUrl = null;
    @observable dataRefreshRequired = false;
    @observable dataset = null;
    @observable djangoFormData = {};

    @action setInitialData() {
        const {initial_data} = this.config,
            settings =
                Object.keys(initial_data.settings).length > 0
                    ? initial_data.settings
                    : this.root.subclass.getDefaultSettings();

        this.djangoFormData = {
            title: initial_data.title,
            slug: initial_data.slug,
            settings: JSON.stringify(settings, null, 2),
            caption: initial_data.caption,
            published: initial_data.published,
        };
        this.root.subclass.setFromJsonSettings(settings, true);
    }
    @action setDjangoForm = djangoForm => {
        this.djangoForm = djangoForm;
    };
    @action updateDjangoFormData = (name, value) => {
        this.djangoFormData[name] = value;
    };
    @action.bound handleSubmit() {
        // make sure our overall tab form is synced
        this.handleTabChange(TABS.OVERALL, this.currentTab);

        // insert the data in this form to the from we submit to the server
        const $form = $(this.djangoForm);
        $form.find("#id_title").val(this.djangoFormData.title);
        $form.find("#id_slug").val(this.djangoFormData.slug);
        $form.find("#id_settings").val(this.djangoFormData.settings);
        $form.find("#id_caption").val(this.djangoFormData.caption);
        $form.find("#id_published").prop("checked", this.djangoFormData.published);
        $form.submit();
    }

    @action.bound handleTabChange(newIndex, lastIndex) {
        // make sure that data cross tabs are synced
        this.currentTab = newIndex;
        switch (lastIndex) {
            case TABS.OVERALL:
                this.root.subclass.setFromJsonSettings(
                    JSON.parse(this.djangoFormData.settings),
                    false
                );
                break;
            case TABS.DATA:
                this.djangoFormData.settings = JSON.stringify(this.root.subclass.settings, null, 2);
                break;
            case TABS.CUSTOMIZATION:
                this.djangoFormData.settings = JSON.stringify(this.root.subclass.settings, null, 2);
                break;
            case TABS.PREVIEW:
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
        return h.hashString(this.djangoFormData.settings);
    }
}

export default BaseStore;
