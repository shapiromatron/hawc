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
    @action handleSubmit() {
        console.log("submit!");
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
