import _ from "lodash";
import {action, computed, toJS, observable} from "mobx";

import h from "shared/utils/helpers";

class MgmtTaskTableStore {
    @observable error = null;
    @observable isFetchingTasks = false;
    @observable tasks = null;
    @observable isFetchingStudies = false;
    @observable studies = null;
    @observable filters = {
        studyTypeFilters: [],
        sortBy: "short_citation",
        orderBy: "asc",
    };
    @observable stagedPatches = {};

    constructor(config) {
        this.config = config;
    }

    @action.bound setError(message) {
        this.error = message;
    }
    @action.bound resetError() {
        this.error = null;
    }
    @action.bound updateFilters(name, value) {
        this.filters[name] = value;
    }
    @action.bound fetchTasks() {
        if (this.isFetchingTasks) {
            return;
        }
        this.isFetchingTasks = true;
        this.resetError();
        fetch(this.config.tasksListUrl, h.fetchGet)
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
        return fetch(this.config.studyListUrl, h.fetchGet)
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
    @action.bound patchTask(task) {
        const url = `${this.config.taskUpdateBaseUrl}${task.id}/`,
            opts = h.fetchPost(this.config.csrf, task, "PATCH");
        fetch(url, opts).then(response => {
            if (response.ok) {
                response.json().then(json => {
                    const index = _.findIndex(this.tasks, {id: json.id});
                    this.tasks[index] = json;
                });
            } else {
                response.json().then(json => this.setError(json));
            }
        });
    }

    @computed get taskListByStudy() {
        const {sortBy, orderBy, studyTypeFilters} = this.filters;
        return _.chain(toJS(this.studies))
            .orderBy([sortBy], [orderBy])
            .filter(study => {
                if (studyTypeFilters.length === 0) {
                    return true;
                }
                return _.some(_.pick(study, studyTypeFilters));
            })
            .map(study => {
                return {
                    tasks: this.tasks
                        .filter(task => task.study.id === study.id)
                        .sort((a, b) => a.type - b.type),
                    study,
                };
            })
            .value();
    }
    @computed get isReady() {
        return this.tasks !== null && this.studies !== null;
    }
}

export default MgmtTaskTableStore;
