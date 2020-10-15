import fetch from "isomorphic-fetch";
import {action, observable} from "mobx";

import h from "shared/utils/helpers";

class TaskAssignmentStore {
    @observable isFetching = false;
    @observable isLoaded = false;
    @observable tasks = [];

    constructor(rootStore, config) {
        this.rootStore = rootStore;
        this.config = config;
    }

    @action.bound fetchTasks() {
        if (this.isFetching) {
            return;
        }

        this.isFetching = true;
        this.isLoaded = false;

        console.log(this.config);
        const url = `${this.config.tasks.url}?assessment_id=${this.config.assessment_id}`;
        return fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.isFetching = false;
                this.isLoaded = true;
                console.log(json);
                this.tasks = json;
            });
    }
}

export default TaskAssignmentStore;
