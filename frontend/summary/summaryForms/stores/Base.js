import fetch from "isomorphic-fetch";
import $ from "$";
import {observable, action, computed} from "mobx";

import h from "shared/utils/helpers";

class BaseStore {
    constructor(rootStore) {
        this.root = rootStore;
    }

    config = null;
    djangoForm = null;

    @observable dataError = null;
    @observable isFetchingData = false;
    @observable dataUrl = null;
    @observable dataRefreshRequired = false;
    @observable dataset = null;
    @observable djangoFormData = {};

    @action setConfig = config => {
        this.config = config;
        this.setInitialData();
    };
    @action setInitialData() {
        const {initial_data} = this.config;
        this.djangoFormData = {
            title: initial_data.title,
            slug: initial_data.slug,
            settings: JSON.stringify(initial_data.settings),
            caption: initial_data.caption,
            published: initial_data.published,
        };
        this.root.subclass.setFromJsonSettings(initial_data.settings, true);
    }
    @action setDjangoForm = djangoForm => {
        this.djangoForm = djangoForm;
    };
    @action updateDjangoFormData = (name, value) => {
        this.djangoFormData[name] = value;
    };
    @action.bound handleSubmit() {
        this.djangoFormData.settings = JSON.stringify(this.root.subclass.settings);
        const $form = $(this.djangoForm);
        $form.find("#id_title").val(this.djangoFormData.title);
        $form.find("#id_slug").val(this.djangoFormData.slug);
        $form.find("#id_settings").val(this.djangoFormData.settings);
        $form.find("#id_caption").val(this.djangoFormData.caption);
        $form.find("#id_published").prop("checked", this.djangoFormData.published);
        $form.submit();
    }

    @action.bound onTabChangeFromOverall() {
        this.root.subclass.setFromJsonSettings(JSON.parse(this.djangoFormData.settings), false);
    }
    @action.bound onTabChangeFromData() {
        this.djangoFormData.settings = JSON.stringify(this.root.subclass.settings);
    }
    @action.bound onTabChangeFigureCustomization() {
        this.djangoFormData.settings = JSON.stringify(this.root.subclass.settings);
    }
    @action.bound onTabChangeFromPreview() {}

    @action.bound getDataset() {
        this.isFetchingData = true;
        fetch(this.dataUrl, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.dataset = json;
                this.dataRefreshRequired = false;
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
