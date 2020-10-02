import _ from "lodash";
import {action, observable} from "mobx";
import h from "shared/utils/helpers";

class TextCleanupStore {
    @observable isLoading = true;
    @observable assessmentMetadata = null;
    @observable cleanupModel = null;
    @observable cleanupField = null;

    constructor(config) {
        this.config = config;
    }

    @action.bound loadAssessmentMetadata() {
        const url = this.config.assessment;

        return fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.assessmentMetadata = json;
                this.isLoading = false;
            })
            .catch(ex => console.error("Assessment parsing failed", ex));
    }

    @action.bound loadCleanupModel(model) {
        console.log("loading cleanup model");
    }
}
export default TextCleanupStore;
