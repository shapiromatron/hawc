import $ from "$";
import {observable, action, computed} from "mobx";

class BaseStore {
    constructor(rootStore) {
        this.root = rootStore;
    }

    config = null;
    djangoForm = null;
    get subclass() {
        return this.root.subclass;
    }

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
        this.subclass.setInitialData(initial_data);
    }
    @action setDjangoForm = djangoForm => {
        this.djangoForm = djangoForm;
    };
    @action updateDjangoFormData = (name, value) => {
        this.djangoFormData[name] = value;
    };
    @action.bound handleSubmit() {
        const $form = $(this.djangoForm);
        $form.find("#id_title").val(this.djangoFormData.title);
        $form.find("#id_slug").val(this.djangoFormData.slug);
        $form.find("#id_settings").val(this.djangoFormData.settings);
        $form.find("#id_caption").val(this.djangoFormData.caption);
        $form.find("#id_published").prop("checked", this.djangoFormData.published);
        $form.submit();
    }

    @action getDataset() {}

    @computed get hasDataset() {
        return this.dataset !== null;
    }
    @computed get isCreate() {
        return this.config.crud === "Create";
    }
}

export default BaseStore;
