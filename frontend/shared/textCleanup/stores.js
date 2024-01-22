import _ from "lodash";
import {action, computed, observable, toJS} from "mobx";
import h from "shared/utils/helpers";

class TextCleanupStore {
    @observable isLoading = true;
    @observable assessmentMetadata = null;
    @observable selectedModel = null;
    @observable modelCleanupFields = null;
    @observable termFieldMapping = null;
    @observable selectedField = null;

    @observable bulkUpdateError = null;
    @observable isLoadingObjects = false;
    @observable objects = null;

    constructor(config) {
        this.config = config;
    }

    @action.bound loadAssessmentMetadata() {
        const url = this.config.assessment;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.assessmentMetadata = json;
                this.isLoading = false;
            })
            .catch(ex => console.error("Assessment parsing failed", ex));
    }
    @action.bound selectModel(model) {
        this.selectedModel = model;
        this.modelCleanupFields = null;
        this.selectedField = null;

        const url = `${model.url_cleanup_list}fields/?assessment_id=${this.config.assessment_id}`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.modelCleanupFields = json.text_cleanup_fields;
                this.termFieldMapping = json.term_field_mapping;
                this.fetchObjects();
            })
            .catch(ex => console.error("Assessment parsing failed", ex));
    }
    @action.bound clearModel() {
        this.selectedModel = null;
        this.modelCleanupFields = null;
        this.selectedField = null;
    }
    @action.bound selectField(field) {
        this.selectedField = field;
    }
    @action.bound clearField() {
        this.selectedField = null;
    }
    @action.bound fetchObjects() {
        this.isLoadingObjects = true;
        this.objects = null;
        const baseUrl = this.selectedModel.url_cleanup_list,
            url = `${baseUrl}?assessment_id=${this.config.assessment_id}`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.isLoadingObjects = false;
                this.objects = json;
            })
            .catch(ex => console.error("Loading objects failed", ex));
    }
    @action.bound submitPatch(ids, payload, groupStore) {
        const url = `${this.selectedModel.url_cleanup_list}?assessment_id=${
                this.config.assessment_id
            }&ids=${ids.join(",")}`,
            opts = h.fetchBulk(this.config.csrf, payload, "PATCH");

        fetch(url, opts)
            .then(response => {
                if (response.ok) {
                    this.bulkUpdateError = null;
                    groupStore.reset();
                    this.updateObjects(ids, payload);
                } else {
                    response.json().then(d => {
                        this.bulkUpdateError = d.detail;
                    });
                }
            })
            .catch(ex => console.error("Patch failed", ex));
    }
    @action.bound updateObjects(ids, payload) {
        const setIds = new Set(ids);
        this.objects
            .filter(obj => setIds.has(obj.id))
            .forEach(obj => {
                _.each(payload, (value, key) => {
                    if (obj[key] !== undefined) {
                        obj[key] = value;
                    }
                });
            });
    }

    @computed get groupedObjects() {
        // group objects by the field to be edited.
        const field = this.selectedField,
            objects = toJS(this.objects),
            fieldTermId = toJS(this.termFieldMapping)[field];
        return _.chain(objects)
            .filter(item => {
                // if the field we want to group on has a term mapping, then only
                // return items which don't have a map ID
                if (fieldTermId !== undefined) {
                    return item[fieldTermId] === null;
                }
                return true;
            })
            .groupBy(item => item[field])
            .sortBy(item => item[0][field].toLowerCase())
            .value();
    }

    @computed get hasTermMapping() {
        return toJS(this.termFieldMapping)[this.selectedField] !== undefined;
    }
}

class GroupStore {
    @observable objects = [];
    @observable expanded = false;
    @observable selectedObjects = new Set();
    @observable currentValue = "";
    @observable editValue = "";

    constructor(rootStore, objects, model, fieldName) {
        // non-observable
        this.rootStore = rootStore;
        this.model = model;
        this.fieldName = fieldName;
        // observable
        this.objects = objects;
        this.currentValue = this.objects[0][fieldName];
        this.editValue = this.currentValue;
    }

    @action.bound submitChanges() {
        const ids = this.expanded ? [...this.selectedObjects] : this.objects.map(d => d.id),
            payload = {};
        payload[this.fieldName] = this.editValue;
        if (ids.length > 0) {
            this.rootStore.submitPatch(ids, payload, this);
        }
    }
    @action.bound toggleExpanded() {
        this.expanded = !this.expanded;
    }
    @action.bound updateValue(newValue) {
        this.editValue = newValue;
    }
    @action.bound toggleSelectAll() {
        const ids = this.allItemsSelected ? [] : this.objects.map(d => d.id);
        this.selectedObjects = new Set(ids);
    }
    @action.bound toggleSelectItem(id) {
        if (this.selectedObjects.has(id)) {
            this.selectedObjects.delete(id);
        } else {
            this.selectedObjects.add(id);
        }
    }
    @action.bound reset() {
        this.expanded = false;
        this.selectedObjects = new Set();
    }

    @computed get allItemsSelected() {
        return this.selectedObjects.size === this.objects.length;
    }
    @computed get fieldNames() {
        return _.chain(this.objects[0]).omit(["id", "ids", "field", "showDetails"]).keys().value();
    }
}

export {GroupStore, TextCleanupStore};
