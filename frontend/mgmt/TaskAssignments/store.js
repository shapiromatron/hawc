import fetch from "isomorphic-fetch";
import {action, observable} from "mobx";

import h from "shared/utils/helpers";

class MgmtTaskAssignmentStore {
    @observable isFetching = false;
    @observable isLoaded = false;
    @observable tasks = [];
    @observable robTasks = [];

    constructor(config) {
        this.config = config;
        this.robTasks = config.rob_tasks;
    }

    @action.bound fetchTasks() {
        if (this.isFetching) {
            return;
        }

        this.isFetching = true;
        this.isLoaded = false;

        const url = `${this.config.tasks.url}?assessment_id=${this.config.assessment_id}`;
        return fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.isFetching = false;
                this.isLoaded = true;
                this.tasks = json;
            });
    }
}

export default MgmtTaskAssignmentStore;
