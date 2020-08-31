import {action, observable} from "mobx";

class Store {
    config = null;
    @observable searchForm = {};
    @observable results = null;
    @observable isSearching = false;

    constructor(config) {
        this.config = config;
        this.searchForm = {
            id: null,
            title: "",
            authors: "",
            journal: "",
            db_id: null,
            abstract: "",
        };
    }

    @action.bound changeSearchTerm(key, value) {
        this.searchForm[key] = value;
    }
    @action.bound search() {
        this.isSearching = true;
    }
}

export default Store;
