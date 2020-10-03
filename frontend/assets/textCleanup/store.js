import {action, observable} from "mobx";
import h from "shared/utils/helpers";

class TextCleanupStore {
    @observable isLoading = true;
    @observable assessmentMetadata = null;
    @observable selectedModel = null;
    @observable modelCleanupFields = null;
    @observable selectedField = null;

    @observable isLoadingObjects = false;
    @observable objects = null;

    constructor(config) {
        this.config = config;
        window.store = this;
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

        const url = `${this.config[model.type].url}fields/?assessment_id=${
            this.config.assessment_id
        }`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.modelCleanupFields = json.text_cleanup_fields;
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
        const baseUrl = this.config[this.selectedModel.type].url,
            url = `${baseUrl}?assessment_id=${this.config.assessment_id}`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.isLoadingObjects = false;
                this.objects = json;
            })
            .catch(ex => console.error("Loading objects failed", ex));
    }
}
export default TextCleanupStore;
