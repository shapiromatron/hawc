import {computed, observable} from "mobx";

class RobAssignmentStore {
    @observable isFetching = false;
    @observable isLoaded = false;

    constructor(rootStore, config) {
        this.rootStore = rootStore;
        this.config = config;
    }

    @computed get showAssessment() {
        return this.config.assessment_id === null;
    }
}

export default RobAssignmentStore;
