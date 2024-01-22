import _ from "lodash";
import {action, computed, observable} from "mobx";
import SmartTagContainer from "shared/smartTags/SmartTagContainer";
import h from "shared/utils/helpers";

import $ from "$";

const getLabelText = function (item) {
    return `${_.repeat("—", item.depth - 1)} ${item.title}`;
};

class SummaryTextStore {
    @observable formData = null;
    @observable formErrors = {};
    @observable items = [];
    @observable selectedId = null;
    @observable isEditing = false;
    @observable isConfirmDelete = false;

    constructor(rootElement, config) {
        this.smartTagContainer = new SmartTagContainer($(rootElement), {showOnStartup: false});
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
        this.formData = {
            title: "",
            slug: "",
            text: "",
            parent: this.items[0].id,
            sibling: null,
        };
        this.formErrors = {};
        this.isEditing = true;
    }
    @action.bound cancelEditing() {
        this.selectedId = null;
        this.isEditing = false;
    }
    @action.bound updateItem(item) {
        const items = this.items.toJS(),
            getParentId = () => {
                const index = _.findIndex(items, d => d.id === item.id);
                let i = index - 1;
                while (i >= 0) {
                    if (items[i].depth === item.depth - 1) {
                        return items[i].id;
                    }
                    i -= 1;
                }
            },
            getSiblingId = () => {
                const index = _.findIndex(items, d => d.id === item.id);
                return items[index - 1].depth === item.depth ? items[index - 1].id : null;
            };

        this.selectedId = item.id;
        this.isEditing = true;
        this.formData = {
            title: item.title,
            slug: item.slug,
            text: item.text,
            parent: getParentId(item),
            sibling: getSiblingId(item),
        };
        this.formErrors = {};
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
            .then(response => {
                if (response.ok) {
                    const id = this.selectedId;
                    this.isConfirmDelete = false;
                    this.isEditing = false;
                    this.selectedId = null;
                    this.items = this.items.filter(item => item.id !== id);
                }
            })
            .catch(ex => console.error("Item delete failed", ex));
    }
    @action.bound createOrUpdate() {
        const url = this.isCreating
                ? `/summary/api/summary-text/`
                : `/summary/api/summary-text/${this.selectedId}/`,
            verb = this.isCreating ? "POST" : "PATCH",
            data = {assessment: this.config.assessment_id, ...this.formData},
            getInsertionIndex = () => {
                const items = this.items.toJS();
                if (this.formData.sibling) {
                    return _.findIndex(items, d => d.id === this.formData.sibling) + 1;
                }
                return _.findIndex(items, d => d.id === this.formData.parent) + 1;
            };
        h.handleSubmit(
            url,
            verb,
            this.config.csrf,
            data,
            item => {
                this.formErrors = {};
                if (this.isCreating) {
                    this.items.splice(getInsertionIndex(), 0, item);
                } else {
                    const items = this.items.toJS(),
                        index = _.findIndex(items, d => d.id === item.id);
                    this.items[index] = item;
                }
                this.isEditing = false;
                this.selectedId = null;
            },
            errors => {
                this.formErrors = errors;
            }
        );
    }
    @action.bound updateFormData(key, value) {
        this.formData[key] = value;
    }
    @action.bound renderSmartTags() {
        this.smartTagContainer.renderAndEnable();
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
    @computed get parentChoices() {
        let choices = this.items.map(item => {
            return {
                id: item.id,
                label: getLabelText(item),
            };
        });
        if (this.selectedId) {
            choices = choices.filter(d => d.id !== this.selectedId);
        }
        choices[0].label = "(document root)";
        return choices;
    }
    @computed get siblingChoices() {
        const items = this.items.toJS(),
            parent = _.find(items, d => d.id === this.formData.parent),
            index = _.findIndex(items, d => d.id === parent.id);
        let i = index + 1,
            children = [{id: "", label: "(none)"}];
        while (i < items.length) {
            if (items[i].depth <= parent.depth) {
                break;
            }
            if (items[i].depth === parent.depth + 1) {
                children.push({id: items[i].id, label: getLabelText(items[i])});
            }
            i += 1;
        }
        return children;
    }
}

export default SummaryTextStore;
