import _ from "lodash";
import {action, computed, toJS, observable} from "mobx";

import h from "shared/utils/helpers";
import Reference from "../Reference";
import TagTree from "../TagTree";

class Store {
    config = null;
    tagtree = null;
    MAX_REFERENCES = 100;

    @observable searchForm = null;
    @observable references = null;
    @observable isSearching = false;

    constructor(config) {
        this.config = config;
        this.tagtree = new TagTree(config.tags[0]);
        this.resetForm();
    }

    @action.bound changeSearchTerm(key, value) {
        this.searchForm[key] = value;
    }
    @action.bound submitSearch() {
        const {assessment_id, csrf} = this.config,
            url = `/lit/api/assessment/${assessment_id}/reference-search/`,
            payload = toJS(this.searchForm),
            tagtree = this.tagtree;

        this.references = null;
        this.isSearching = true;

        // remove blank items from query
        _.each(payload, (value, key) => {
            if (value === "") {
                delete payload[key];
            }
        });
        return fetch(url, h.fetchPost(csrf, payload, "POST"))
            .then(resp => resp.json())
            .then(json => {
                this.references = json.references.map(d => new Reference(d, tagtree));
                this.isSearching = false;
            })
            .catch(ex => console.error("Search failed", ex));
    }
    @action.bound resetForm() {
        this.isSearching = false;
        this.searchForm = {
            id: "",
            db_id: "",
            year: "",
            title: "",
            authors: "",
            journal: "",
            abstract: "",
            tags: [],
        };
        this.references = null;
    }

    @computed get hasReferences() {
        return this.references !== null;
    }
    @computed get numReferences() {
        return this.references !== null ? this.references.length : 0;
    }
}

export default Store;
