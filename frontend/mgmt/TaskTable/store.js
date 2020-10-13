import fetch from "isomorphic-fetch";
import {action, observable} from "mobx";

import h from "shared/utils/helpers";

class MgmtTaskTableStore {
    @observable error = null;
    @observable isFetchingTasks = false;
    @observable tasks = null;
    @observable isFetchingStudies = false;
    @observable studies = null;

    constructor(config) {
        this.config = config;
    }

    @action.bound setError(message) {
        this.error = message;
    }
    @action.bound resetError() {
        this.error = null;
    }
    @action.bound fetchTasks() {
        if (this.isFetchingTasks) {
            return;
        }
        this.isFetchingTasks = true;
        this.resetError();
        const url = `${this.config.tasks_url}?assessment_id=${this.config.assessment_id}`;
        fetch(url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.tasks = json;
                this.isFetchingTasks = false;
            })
            .catch(error => {
                this.setError(error);
                this.isFetchingTasks = false;
            });
    }
    @action.bound fetchStudies() {
        if (this.isFetchingStudies) {
            return;
        }
        this.isFetchingStudies = true;
        this.resetError();
        return fetch(this.config.studies.url, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.studies = json;
                this.isFetchingStudies = false;
            })
            .catch(error => {
                this.setError(error);
                this.isFetchingStudies = false;
            });
    }
}

export default MgmtTaskTableStore;
