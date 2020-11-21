import _ from "lodash";
import {action, computed, observable} from "mobx";

import h from "shared/utils/helpers";

class SummaryTextStore {
    @observable formData = null;
    @observable formErrors = {};
    @observable items = [];
    @observable selectedId = null;
    @observable isEditing = false;
    @observable isConfirmDelete = false;

    constructor(config) {
        this.config = config;
    }

    @action.bound fetchItems() {
        const url = `/summary/api/summary-text/?assessment_id=${this.config.assessment_id}`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.items = json;
            })
            .catch(ex => console.error("Item fetching failed", ex));
    }

    @action.bound createItem() {
        this.selectedId = null;
        this.isEditing = true;
        this.formData = {
            title: "",
            slug: "",
            text: "",
            parent: "---",
            sibling: "---",
        };
    }
    @action.bound cancelEditing() {
        this.selectedId = null;
        this.isEditing = false;
    }
    @action.bound updateItem(item) {
        this.selectedId = item.id;
        this.isEditing = true;
        this.formData = {
            title: item.title,
            slug: item.slug,
            text: item.text,
            parent: item.parent,
            sibling: item.sibling,
        };
    }
    @action.bound clickConfirmDelete() {
        this.isConfirmDelete = true;
    }
    @action.bound cancelConfirmDelete() {
        this.isConfirmDelete = false;
    }
    @action.bound deleteItem() {
        const url = `/summary/api/summary-text/${this.selectedId}/`;
        fetch(url, h.fetchDelete(this.config.csrf))
            .then(response => response.json())
            .then(json => {
                this.items = this.items.filter(item => item.id != this.selectedId);
                this.isEditing = false;
                this.selectedId = null;
            })
            .catch(ex => console.error("Item delete failed", ex));
    }
    @action.bound createOrUpdate() {
        const url = `/summary/api/summary-text/`,
            data = {assessment: this.config.assessment_id, ...this.formData};
        h.handleSubmit(
            url,
            "POST",
            this.config.csrf,
            data,
            item => {
                this.formErrors = {};
                this.items.append(item);
                this.isEditing = false;
                this.selectedId = null;
            },
            errors => {
                this.formErrors = errors;
                this.formErrors.parent = ["this one is a dud."];
            }
        );
    }
    @action.bound updateFormData(key, value) {
        this.formData[key] = value;
    }

    @computed get hasItems() {
        return this.items.length > 0;
    }
    @computed get visibleItems() {
        return this.items.filter(item => item.depth > 1);
    }
    @computed get isCreating() {
        return this.isEditing && this.selectedId === null;
    }
}

export default SummaryTextStore;
